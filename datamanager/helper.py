# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from elasticsearch.exceptions import TransportError

from rq import Connection
from rq.job import Job
from rq.registry import StartedJobRegistry
from redis import Redis

from collections import defaultdict
from itertools import groupby

from datamanager.errors import FileDoesNotExistError, ThereIsPreviousJobUploadingTheFileError, ThereIsNotActiveJobError
from datamanager.models import UploaderJobExecution, LoadFile, DataSourcePath

from rqworkers.tasks import upload_file_job

from esapi.helper.profile import ESProfileHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.resume import ESResumeStatisticHelper

import io
import glob
import os
import zipfile


class UploaderManager(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.index = self.file_name.split('.')[1]

    def upload_data(self):
        with transaction.atomic():
            if LoadFile.objects.filter(fileName=self.file_name).exists():
                file_path_obj = LoadFile.objects.get(fileName=self.file_name)
            else:
                raise FileDoesNotExistError()

            # check if exist job associate to file obj
            if UploaderJobExecution.objects.filter(file=file_path_obj).filter(
                    Q(status=UploaderJobExecution.ENQUEUED) | Q(status=UploaderJobExecution.RUNNING)).exists():
                raise ThereIsPreviousJobUploadingTheFileError()

            file_path = os.path.join(file_path_obj.dataSourcePath, self.file_name)
            job = upload_file_job.delay(file_path)
            UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(), status=UploaderJobExecution.ENQUEUED,
                                                file=file_path_obj, jobId=job.id)

    def delete_data(self):
        helpers = [(DataSourcePath.STOP, ESStopHelper),
                   (DataSourcePath.PROFILE, ESProfileHelper),
                   (DataSourcePath.SPEED, ESSpeedHelper),
                   (DataSourcePath.TRIP, ESTripHelper),
                   (DataSourcePath.SHAPE, ESShapeHelper),
                   (DataSourcePath.OD_BY_ROUTE, ESODByRouteHelper),
                   (DataSourcePath.GENERAL, ESResumeStatisticHelper)]

        index_helper = None
        for index_id, helper in helpers:
            if self.index == index_id:
                index_helper = helper
                break

        es_query = index_helper().delete_data_by_file(self.file_name)
        result = es_query.execute()

        return result.total

    def cancel_uploading(self):
        with transaction.atomic():
            enqueued_or_running = Q(status=UploaderJobExecution.ENQUEUED) | Q(status=UploaderJobExecution.RUNNING)
            if not UploaderJobExecution.objects.filter(enqueued_or_running, file__fileName=self.file_name).exists():
                raise ThereIsNotActiveJobError()
            job_obj = UploaderJobExecution.objects.get(enqueued_or_running, file__fileName=self.file_name)

            # rq connection
            queue_name = 'data_uploader'
            host = settings.RQ_QUEUES[queue_name]['HOST']
            port = settings.RQ_QUEUES[queue_name]['PORT']
            with Connection(Redis(host, port)) as redis_conn:
                registry = StartedJobRegistry('default', connection=redis_conn)
                job = Job.fetch(str(job_obj.jobId), connection=redis_conn)
                # if job started, kill it (stop process)
                if job_obj.jobId in registry.get_job_ids():
                    job.kill()
                job.delete()
            job_obj.status = UploaderJobExecution.CANCELED
            job_obj.executionEnd = timezone.now()
            job_obj.save()

            # delete data uploaded previous to cancel
            self.delete_data()


class FileManager(object):

    def __init__(self):
        pass

    def _get_file_object(self, file_path):
        """
        :param file_path: file path will upload
        :return: file object
        """
        if zipfile.is_zipfile(file_path):
            zip_file_obj = zipfile.ZipFile(file_path, 'r')
            # it assumes that zip file has only one file
            file_name = zip_file_obj.namelist()[0]
            file_obj = zip_file_obj.open(file_name, 'rU')
        else:
            file_obj = io.open(file_path, str('rb'))

        return file_obj

    def _count_doc_in_file(self, data_source_code, file_path):
        i = 0
        with self._get_file_object(file_path) as f:
            if data_source_code in [DataSourcePath.SHAPE, DataSourcePath.STOP]:
                for group_id, __ in groupby(f, lambda row: row.split(str('|'))[0]):
                    # lines with hyphen on first column are bad lines and must not be considered
                    if group_id != '-':
                        i += 1
                # not count header
                i -= 1
            else:
                # how it starts from zero is not count header
                for i, _ in enumerate(f):
                    pass
        return i

    def _get_file_list(self):
        """ list all files in directory with a given code """
        file_dict = defaultdict(list)

        for data_source_obj in DataSourcePath.objects.all():
            path = data_source_obj.path
            # TODO: if is running on windows, remove this
            if os.name == 'nt':
                path = os.path.join(settings.BASE_DIR, 'media')

            path_name = os.path.join(path, data_source_obj.filePattern)
            zipped_path_name = os.path.join(path, '{0}.zip'.format(data_source_obj.filePattern))
            file_name_list = glob.glob(path_name) + glob.glob(zipped_path_name)

            for file_path in file_name_list:
                file_name = os.path.basename(file_path)
                last_modified = timezone.make_aware(timezone.datetime.fromtimestamp(os.path.getmtime(file_path)))
                file_obj, created = LoadFile.objects.get_or_create(fileName=file_name, defaults={
                    'dataSourcePath': path,
                    'discoveredAt': timezone.now(),
                    'lastModified': last_modified
                })
                if created or last_modified != file_obj.lastModified:
                    file_obj.lines = self._count_doc_in_file(data_source_obj.code, file_path)
                file_obj.dataSourcePath = path
                file_obj.save()
                serialized_file = file_obj.get_dictionary()
                file_dict[data_source_obj.code].append(serialized_file)

        return file_dict

    def _get_document_number_by_file_from_elasticsearch(self):
        helpers = [(DataSourcePath.STOP, ESStopHelper),
                   (DataSourcePath.PROFILE, ESProfileHelper),
                   (DataSourcePath.SPEED, ESSpeedHelper),
                   (DataSourcePath.TRIP, ESTripHelper),
                   (DataSourcePath.SHAPE, ESShapeHelper),
                   (DataSourcePath.OD_BY_ROUTE, ESODByRouteHelper),
                   (DataSourcePath.GENERAL, ESResumeStatisticHelper)]
        queries = {}
        index_helper_instance = None
        for index_id, helper in helpers:
            index_helper_instance = helper()
            queries[index_id] = index_helper_instance.get_data_by_file()

        doc_number_by_file = {}
        try:
            answer = index_helper_instance.make_multisearch_query_for_aggs(queries)

            for key in answer:
                files = answer[key]['aggregations']['files']['buckets']
                for data_file in files:
                    doc_number_by_file[data_file['key']] = data_file['doc_count']
        except TransportError as e:
            if e.error != 'index_not_found_exception':
                raise e

        return doc_number_by_file

    def get_file_list(self):
        uploaded_files = self._get_document_number_by_file_from_elasticsearch()
        file_list = self._get_file_list()

        for key in file_list:
            for data_file in file_list[key]:
                del data_file['path']
                data_file['docNumber'] = uploaded_files[data_file['name']] if data_file['name'] in uploaded_files else 0

        return file_list
