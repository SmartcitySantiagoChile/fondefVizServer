# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from rq import Connection
from redis import Redis

from collections import defaultdict

from datamanager.errors import FileDoesNotExistError, ThereIsPreviousJobUploadingTheFileError, \
    ThereIsNotActiveJobError, ThereIsPreviousJobExporterDataError
from datamanager.models import UploaderJobExecution, LoadFile, DataSourcePath, ExporterJobExecution

from rqworkers.tasks import upload_file_job, export_data_job, count_line_of_file_job
from rqworkers.killClass import KillJob
from rqworkers.dataDownloader.csvhelper.profile import ProfileByExpeditionData, ProfileDataByStop
from rqworkers.dataDownloader.csvhelper.odbyroute import OdByRouteData
from rqworkers.dataDownloader.csvhelper.speed import SpeedData
from rqworkers.dataDownloader.csvhelper.trip import TripData
from rqworkers.dataDownloader.errors import UnrecognizedDownloaderNameError

from esapi.helper.profile import ESProfileHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.resume import ESResumeStatisticHelper

import glob
import os
import rqworkers.dataDownloader.csvhelper.helper as csv_helper


def get_util_helpers(file_path):
    """ return a list of helpers that match with file extension """
    file_extension = os.path.basename(file_path).split('.')[1]

    helpers = [
        ESStopByRouteHelper(),
        ESStopHelper(),
        ESProfileHelper(),
        ESSpeedHelper(),
        ESTripHelper(),
        ESShapeHelper(),
        ESODByRouteHelper(),
        ESResumeStatisticHelper()
    ]

    result_helpers = []

    for helper in helpers:
        if file_extension in helper.file_extensions:
            result_helpers.append(helper)

    return result_helpers


class ExporterManager(object):

    def __init__(self, es_query):
        # Search instance
        self.es_query = es_query

    def export_data(self, downloader, user):
        with transaction.atomic():
            # check if exist job associate to file obj
            human_readable_query = str(self.es_query.to_dict()).replace('u\'', '"').replace('\'', '"')
            if ExporterJobExecution.objects.filter(query=human_readable_query, user=user).filter(
                    Q(status=ExporterJobExecution.ENQUEUED) | Q(status=ExporterJobExecution.RUNNING)).exists():
                raise ThereIsPreviousJobExporterDataError()

            # Determine file type according to index name
            if downloader == csv_helper.OD_BY_ROUTE_DATA:
                downloader_instance = OdByRouteData(self.es_query.to_dict())
                file_type = ExporterJobExecution.OD_BY_ROUTE
            elif downloader == csv_helper.PROFILE_BY_EXPEDITION_DATA:
                downloader_instance = ProfileByExpeditionData(self.es_query.to_dict())
                file_type = ExporterJobExecution.PROFILE
            elif downloader == csv_helper.PROFILE_BY_STOP_DATA:
                downloader_instance = ProfileDataByStop(self.es_query.to_dict())
                file_type = ExporterJobExecution.PROFILE
            elif downloader == csv_helper.SPEED_MATRIX_DATA:
                downloader_instance = SpeedData(self.es_query.to_dict())
                file_type = ExporterJobExecution.SPEED
            elif downloader == csv_helper.TRIP_DATA:
                downloader_instance = TripData(self.es_query.to_dict())
                file_type = ExporterJobExecution.TRIP
            else:
                raise UnrecognizedDownloaderNameError()

            # TODO: if is running on windows, we do not use async tasks
            export_func = export_data_job if os.name == 'nt' else export_data_job.delay
            job = export_func(self.es_query.to_dict(), downloader)
            ExporterJobExecution.objects.create(enqueueTimestamp=timezone.now(), jobId=job.id, fileType=file_type,
                                                status=ExporterJobExecution.ENQUEUED, query=human_readable_query,
                                                user=user, filters=downloader_instance.get_filters())


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

            # TODO: if is running on windows, we do not use async tasks
            upload_func = upload_file_job if os.name == 'nt' else upload_file_job.delay
            job = upload_func(file_path, [helper.index_name for helper in get_util_helpers(file_path)])

            UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(), jobId=job.id,
                                                status=UploaderJobExecution.ENQUEUED, file=file_path_obj)

            # update data
            file_path_obj = LoadFile.objects.get(fileName=self.file_name)
            return file_path_obj

    def delete_data(self):
        result = None
        for helper in get_util_helpers(self.file_name):
            result = helper.delete_data_by_file(self.file_name)

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
                    # TODO: if is running on windows, we do not use async tasks
                    count_func = count_line_of_file_job if os.name == 'nt' else count_line_of_file_job.delay
                    count_func(file_obj, data_source_obj.indexName, file_path)
                    file_obj.lastModified = last_modified
                file_obj.dataSourcePath = path
                file_obj.save()
                serialized_file = file_obj.get_dictionary()
                file_dict[data_source_obj.indexName].append(serialized_file)

        return file_dict

    def get_document_number_by_file_from_elasticsearch(self, file_filter=None):
        helpers = [
            ESStopHelper(),
            ESStopByRouteHelper(),
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
            files = helper.get_data_by_file(file_filter=file_name_list).execute().aggregations.files.buckets
            for data_file in files:
                doc_number_by_file[data_file.key] = data_file.doc_count

        return doc_number_by_file

    def get_file_list(self):
        uploaded_files = self.get_document_number_by_file_from_elasticsearch()
        file_list = self._get_file_list()

        for key in file_list:
            for data_file in file_list[key]:
                data_file['docNumber'] = uploaded_files[data_file['name']] if data_file['name'] in uploaded_files else 0

        return file_list
