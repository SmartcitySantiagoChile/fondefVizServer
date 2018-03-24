# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from rq import Connection
from redis import Redis

from collections import defaultdict
from itertools import groupby

from datamanager.errors import FileDoesNotExistError, ThereIsPreviousJobUploadingTheFileError, ThereIsNotActiveJobError, \
    ThereIsPreviousJobExporterDataError
from datamanager.models import UploaderJobExecution, LoadFile, DataSourcePath, ExporterJobExecution

from rqworkers.tasks import upload_file_job, export_data_job
from rqworkers.killClass import KillJob

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


class ExporterManager(object):

    def __init__(self, es_query):
        # Search instance
        self.es_query = es_query

    def export_data(self, downloader, user):
        with transaction.atomic():
            # check if exist job associate to file obj
            human_readable_query = str(self.es_query.to_dict()).replace('u\'', '"').replace('\'', '"')
            if ExporterJobExecution.objects.filter(query=human_readable_query).filter(
                    Q(status=ExporterJobExecution.ENQUEUED) | Q(status=ExporterJobExecution.RUNNING)).exists():
                raise ThereIsPreviousJobExporterDataError()

            job = export_data_job.delay(self.es_query.to_dict(), downloader)
            ExporterJobExecution.objects.create(enqueueTimestamp=timezone.now(), jobId=job.id,
                                                status=ExporterJobExecution.ENQUEUED,
                                                query=human_readable_query, user=user)


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
            UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(), jobId=job.id,
                                                status=UploaderJobExecution.ENQUEUED, file=file_path_obj)

            # update data
            file_path_obj = LoadFile.objects.get(fileName=self.file_name)
            return file_path_obj

    def delete_data(self):
        helpers = [
            ESStopHelper(),
            ESProfileHelper(),
            ESSpeedHelper(),
            ESTripHelper(),
            ESShapeHelper(),
            ESODByRouteHelper(),
            ESResumeStatisticHelper()
        ]

        index_helper = None
        for helper in helpers:
            if self.index == helper.get_index_name():
                index_helper = helper
                break

        result = index_helper.delete_data_by_file(self.file_name)

        if result is not None:
            result = result.total

        return result

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
                job = KillJob.fetch(str(job_obj.jobId), connection=redis_conn)
                job.kill()
                job.delete()
            job_obj.status = UploaderJobExecution.CANCELED
            job_obj.executionEnd = timezone.now()
            job_obj.save()

            # delete data uploaded previous to cancel
            self.delete_data()

            # update data
            file_path_obj = LoadFile.objects.get(fileName=self.file_name)
            return file_path_obj


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
            if data_source_code in [ESShapeHelper().get_index_name(), ESStopHelper().get_index_name()]:
                for group_id, __ in groupby(f, lambda row: row.split(str('|'))[0]):
                    # lines with hyphen on first column are bad lines and must not be considered
                    if group_id != str('-'):
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
                    file_obj.lines = self._count_doc_in_file(data_source_obj.indexName, file_path)
                    file_obj.lastModified = last_modified
                file_obj.dataSourcePath = path
                file_obj.save()
                serialized_file = file_obj.get_dictionary()
                file_dict[data_source_obj.indexName].append(serialized_file)

        return file_dict

    def get_document_number_by_file_from_elasticsearch(self, file_filter=None):
        helpers = [
            ESStopHelper(),
            ESProfileHelper(),
            ESSpeedHelper(),
            ESTripHelper(),
            ESShapeHelper(),
            ESODByRouteHelper(),
            ESResumeStatisticHelper()
        ]

        file_name_list = None
        if file_filter is not None:
            if isinstance(file_filter, list):
                file_name_list = file_filter
            else:
                file_name_list = [file_filter]

        doc_number_by_file = {}
        for helper in helpers:
            files = helper.get_data_by_file(filter=file_name_list).execute().aggregations.files.buckets
            for data_file in files:
                doc_number_by_file[data_file['key']] = data_file['doc_count']

        return doc_number_by_file

    def get_file_list(self):
        uploaded_files = self.get_document_number_by_file_from_elasticsearch()
        file_list = self._get_file_list()

        for key in file_list:
            for data_file in file_list[key]:
                data_file['docNumber'] = uploaded_files[data_file['name']] if data_file['name'] in uploaded_files else 0

        return file_list
