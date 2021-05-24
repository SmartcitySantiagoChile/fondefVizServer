# -*- coding: utf-8 -*-


import os
from collections import defaultdict

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from redis import Redis
from rq import Connection

import dataDownloader.csvhelper.helper as csv_helper
from dataDownloader.csvhelper.bip import BipData
from dataDownloader.csvhelper.odbyroute import OdByRouteData
from dataDownloader.csvhelper.paymentfactor import PaymentFactorData
from dataDownloader.csvhelper.profile import ProfileByExpeditionData, ProfileDataByStop
from dataDownloader.csvhelper.speed import SpeedDataWithFormattedShape
from dataDownloader.csvhelper.trip import TripData
from dataDownloader.errors import UnrecognizedDownloaderNameError
from datamanager.errors import FileDoesNotExistError, ThereIsPreviousJobUploadingTheFileError, \
    ThereIsNotActiveJobError, ThereIsPreviousJobExporterDataError
from datamanager.models import UploaderJobExecution, LoadFile, ExporterJobExecution
from esapi.helper.bip import ESBipHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.opdata import ESOPDataHelper
from esapi.helper.paymentfactor import ESPaymentFactorHelper
from esapi.helper.profile import ESProfileHelper
from esapi.helper.resume import ESResumeStatisticHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.trip import ESTripHelper
from rqworkers.killClass import KillJob
from rqworkers.tasks import upload_file_job, export_data_job


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
        ESResumeStatisticHelper(),
        ESPaymentFactorHelper(),
        ESBipHelper(),
        ESOPDataHelper()
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
                downloader_instance = SpeedDataWithFormattedShape(self.es_query.to_dict())
                file_type = ExporterJobExecution.SPEED
            elif downloader == csv_helper.TRIP_DATA:
                downloader_instance = TripData(self.es_query.to_dict())
                file_type = ExporterJobExecution.TRIP
            elif downloader == csv_helper.PAYMENT_FACTOR_DATA:
                downloader_instance = PaymentFactorData(self.es_query.to_dict())
                file_type = ExporterJobExecution.PAYMENT_FACTOR
            elif downloader == csv_helper.BIP_DATA:
                downloader_instance = BipData(self.es_query.to_dict())
                file_type = ExporterJobExecution.BIP

            else:
                raise UnrecognizedDownloaderNameError()

            job = export_data_job.delay(self.es_query.to_dict(), downloader)
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
            job = upload_file_job.delay(file_path, [helper.index_name for helper in get_util_helpers(file_path)])

            UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(), jobId=job.id,
                                                status=UploaderJobExecution.ENQUEUED, file=file_path_obj)

            # update data
            file_path_obj = LoadFile.objects.get(fileName=self.file_name)
            return file_path_obj

    def delete_data(self):
        result = None
        error_instance = None
        for helper in get_util_helpers(self.file_name):
            try:
                result = helper.delete_data_by_file(self.file_name)
            except Exception as e:
                error_instance = e

        finished_or_canceled = Q(status=UploaderJobExecution.FINISHED) | Q(status=UploaderJobExecution.CANCELED)
        UploaderJobExecution.objects.filter(finished_or_canceled, file__fileName=self.file_name,
                                            wasDeletedAt__isnull=True).update(wasDeletedAt=timezone.now())

        if error_instance is not None:
            raise error_instance

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

    def _get_file_list(self, index_filter=None):
        """ list all files in directory with a given code """
        file_dict = defaultdict(list)
        if index_filter:
            query = Q()
            for index in index_filter:
                query |= Q(fileName__contains=index)
            objects = LoadFile.objects.filter(query)
        else:
            objects = LoadFile.objects.all()

        for file_obj in objects:
            serialized_file = file_obj.get_dictionary()
            index_name = file_obj.fileName.split('.')[1]
            file_dict[index_name].append(serialized_file)

        return file_dict

    def get_document_number_by_file_from_elasticsearch(self, file_filter=None, index_filter=None):
        helpers_dict = {
            'stop': ESStopHelper(),
            'stopbyroute': ESStopByRouteHelper(),
            'profile': ESProfileHelper(),
            'speed': ESSpeedHelper(),
            'trip': ESTripHelper(),
            'shape': ESShapeHelper(),
            'odbyroute': ESODByRouteHelper(),
            'general': ESResumeStatisticHelper(),
            'paymentfactor': ESPaymentFactorHelper(),
            'bip': ESBipHelper(),
            'opdata': ESOPDataHelper()
        }

        if index_filter is not None:
            helpers = []
            for index in index_filter:
                if index in helpers_dict:
                    helpers.append(helpers_dict[index])
        else:
            helpers = list(helpers_dict.values())

        if file_filter is not None:
            if isinstance(file_filter, list):
                file_name_list = file_filter
            else:
                file_name_list = [file_filter]
        else:
            file_name_list = None
        doc_number_by_file = {}
        for helper in helpers:
            files = helper.get_data_by_file(file_filter=file_name_list).execute().aggregations.files.buckets
            for data_file in files:
                doc_number_by_file[data_file.key] = data_file.doc_count

        return doc_number_by_file

    def get_file_list(self, index_filter=None):
        upload_filter = index_filter.copy() if index_filter else None
        if upload_filter and 'stop' in upload_filter:
            upload_filter.remove('stop')
            upload_filter.append('stopbyroute')
        uploaded_files = self.get_document_number_by_file_from_elasticsearch(index_filter=upload_filter)
        file_list = self._get_file_list(index_filter=index_filter)
        for key in file_list:
            for data_file in file_list[key]:
                data_file['docNumber'] = uploaded_files[data_file['name']] if data_file['name'] in uploaded_files else 0

        return file_list

    def get_time_period_list_by_file_from_elasticsearch(self, index_filter=None):
        """
        Get a dict with time_period list per file
        Args:
            index_filter: index to filter query
        Returns:
            dict
        """
        helpers_dict = {
            'profile': ESProfileHelper(),
            'odbyroute': ESODByRouteHelper(),
            'trip': ESTripHelper()
        }

        if index_filter is not None:
            helpers = []
            for index in index_filter:
                if index in helpers_dict:
                    helpers.append(helpers_dict[index])
        else:
            helpers = list(helpers_dict.values())

        time_period_by_date_dict = defaultdict(lambda: defaultdict(list))
        for helper in helpers:
            file_list = helper.get_all_time_periods().execute().aggregations.to_dict()["time_periods_per_file"][
                "buckets"]
            for file in file_list:
                file_name = file['key']
                date, index = file_name.split('.')[:2]
                # skip 2 keys
                time_period_list = set()
                for i in range(len(file.keys()) - 2):
                    time_period_list_aux = set(
                        time_period["key"] for time_period in file[f"time_periods_{i}"]["buckets"])
                    time_period_list = time_period_list.union(time_period_list_aux)
                time_period_by_date_dict[date][index] = list(time_period_list)
        return time_period_by_date_dict
