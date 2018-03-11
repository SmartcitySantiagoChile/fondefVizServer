# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from collections import defaultdict
from itertools import groupby

from esapi.helper.profile import ESProfileHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.resume import ESResumeStatisticHelper
from esapi.errors import GenericError

from rqworkers.dataUploader.errors import IndexNotEmptyError
from rqworkers.tasks import upload_file_job

from datamanager.errors import FileDoesNotExistError, ThereIsPreviousJobUploadingTheFileError, IndexWithDocumentError, \
    BadFormatDocumentError, ThereIsNotActiveJobError
from datamanager.models import DataSourcePath, LoadFile, UploaderJobExecution
from datamanager.messages import JobEnqueued, DataDeletedSuccessfully, JobCanceledSuccessfully

from rq.exceptions import NoSuchJobError
from rq import Connection
from rq.job import Job
from rq.registry import StartedJobRegistry
from redis import Redis

import os
import glob
import io
import zipfile


class LoadManagerHTML(View):
    """ load  web page to load files """

    def get(self, request):
        template = 'datamanager/loadManager.html'

        # define the order table appear in web page
        tables = [
            {
                'bubble_title': '', 'bubble_content': 'Archivo de perfiles de carga',
                'id': 'profileTable', 'title_icon': 'fa-bus', 'title': 'Perfiles'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivos de velocidades',
                'id': 'speedTable', 'title_icon': 'fa-tachometer', 'title': 'Velocidades'
            },
            {
                'bubble_title': '', 'bubble_content': 'Información de las etapas hechas por usuario en cada servicio.',
                'id': 'odbyrouteTable', 'title_icon': 'fa-map-o', 'title': 'etapas por servicio'
            },
            {
                'bubble_title': '', 'bubble_content': 'Datos de la ejecución de adatrap',
                'id': 'generalTable', 'title_icon': 'fa-clone', 'title': 'Datos generales'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivos de viajes',
                'id': 'travelTable', 'title_icon': 'fa-line-chart', 'title': 'Viajes'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivo con geometría de servicios',
                'id': 'shapeTable', 'title_icon': 'fa-code-fork', 'title': 'Geometria de servicios'
            },
            {
                'bubble_title': '', 'bubble_content': 'Archivo con secuencia de paradas por servicio',
                'id': 'stopTable', 'title_icon': 'fa-map-marker', 'title': 'Secuencia de paradas'
            }
        ]
        context = {
            'tables': tables
        }

        return render(request, template, context)


class LoadData(View):
    """ Load data to elastic search """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadData, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            with transaction.atomic():
                if LoadFile.objects.filter(fileName=file_name).exists():
                    file_path_obj = LoadFile.objects.get(fileName=file_name)
                else:
                    raise FileDoesNotExistError()

                # check if exist job associate to file obj
                if UploaderJobExecution.objects.filter(file=file_path_obj).filter(
                        Q(status=UploaderJobExecution.ENQUEUED) | Q(status=UploaderJobExecution.RUNNING)).exists():
                    raise ThereIsPreviousJobUploadingTheFileError()

                file_path = os.path.join(file_path_obj.dataSourcePath, file_name)
                job = upload_file_job.delay(file_path)
                UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(),
                                                    status=UploaderJobExecution.ENQUEUED,
                                                    file=file_path_obj, jobId=job.id)

            response['status'] = JobEnqueued().get_status_response()
        except GenericError as e:
            response['status'] = e.get_status_response()
        except IndexNotEmptyError:
            response['status'] = IndexWithDocumentError().get_status_response()

        return JsonResponse(response)


class DeleteData(View):
    """ Delete data from elastic search """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteData, self).dispatch(request, *args, **kwargs)

    def delete_data(self, file_name):
        index = file_name.split('.')[1]

        index_helper = None

        if index == DataSourcePath.STOP:
            index_helper = ESStopHelper
        elif index == DataSourcePath.PROFILE:
            index_helper = ESProfileHelper
        elif index == DataSourcePath.SPEED:
            index_helper = ESSpeedHelper
        elif index == DataSourcePath.TRIP:
            index_helper = ESTripHelper
        elif index == DataSourcePath.SHAPE:
            index_helper = ESShapeHelper
        elif index == DataSourcePath.OD_BY_ROUTE:
            index_helper = ESODByRouteHelper
        elif index == DataSourcePath.GENERAL:
            index_helper = ESResumeStatisticHelper

        es_query = index_helper().delete_data_by_file(file_name)
        result = es_query.execute()

        return result.total

    def post(self, request):
        """  """
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            deleted_doc_number = self.delete_data(file_name)
            response['status'] = DataDeletedSuccessfully(deleted_doc_number).get_status_response()
        except IndexError:
            response['status'] = BadFormatDocumentError().get_status_response()

        return JsonResponse(response)


class CancelData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CancelData, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            with transaction.atomic():
                if not UploaderJobExecution.objects.filter(file__fileName=file_name).filter(
                        Q(status=UploaderJobExecution.ENQUEUED) | Q(status=UploaderJobExecution.RUNNING)).exists():
                    raise ThereIsNotActiveJobError()
                job_obj = UploaderJobExecution.objects.get(
                    Q(status=UploaderJobExecution.ENQUEUED) | Q(status=UploaderJobExecution.RUNNING),
                    file__fileName=file_name)

                queue_name = 'data_uploader'
                host = settings.RQ_QUEUES[queue_name]['HOST']
                port = settings.RQ_QUEUES[queue_name]['PORT']
                with Connection(Redis(host, port)) as redis_conn:
                    registry = StartedJobRegistry('default', connection=redis_conn)
                    job = Job.fetch(str(job_obj.jobId), connection=redis_conn)
                    if job_obj.jobId in registry.get_job_ids():
                        job.kill()
                    job.delete()
                job_obj.status = UploaderJobExecution.CANCELED
                job_obj.executionEnd = timezone.now()
                job_obj.save()

                # delete data uploaded previous to cancel
                DeleteData().delete_data(file_name)

            response['status'] = JobCanceledSuccessfully().get_status_response()
        except GenericError as e:
            response['status'] = e.get_status_response()
        except NoSuchJobError:
            response['status'] = ThereIsNotActiveJobError().get_status_response()
        except IndexError:
            response['status'] = BadFormatDocumentError().get_status_response()

        return JsonResponse(response)


class GetLoadFileData(View):
    """ """

    def get_file_object(self, file_path):
        """
        :param kwargs: dictionary to give encoding param
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

    def count_doc_in_file(self, data_source_obj, file_path):
        i = 0
        with self.get_file_object(file_path) as f:
            if data_source_obj.code in [DataSourcePath.SHAPE, DataSourcePath.STOP]:
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

    def get_file_list(self):
        """ list all files in directory with code """
        file_dict = defaultdict(list)

        for data_source_obj in DataSourcePath.objects.all():
            path = data_source_obj.path
            # if is running on windows
            if os.name == 'nt':
                path = os.path.join(settings.BASE_DIR, 'media')

            path_name = os.path.join(path, data_source_obj.filePattern)
            zipped_path_name = os.path.join(path, '{0}.zip'.format(data_source_obj.filePattern))
            file_name_list = glob.glob(path_name) + glob.glob(zipped_path_name)

            for file_path in file_name_list:
                file_name = os.path.basename(file_path)
                file_obj, created = LoadFile.objects.get_or_create(fileName=file_name, defaults={
                    'dataSourcePath': path,
                    'discoveredAt': timezone.now(),
                    'lastModified': os.path.getmtime(file_path)
                })
                if created or os.path.getmtime(file_path) :
                    file_obj.lines = self.count_doc_in_file(data_source_obj, file_path)
                else:
                    file_obj.dataSourcePath = path
                file_obj.save()
                serialized_file = file_obj.get_dictionary()
                file_dict[data_source_obj.code].append(serialized_file)

        return file_dict

    def get_uploaded_files(self):
        index_helper_list = [ESProfileHelper, ESSpeedHelper, ESODByRouteHelper, ESTripHelper, ESStopHelper,
                             ESShapeHelper]
        key_list = [DataSourcePath.PROFILE, DataSourcePath.SPEED, DataSourcePath.OD_BY_ROUTE, DataSourcePath.TRIP,
                    DataSourcePath.STOP, DataSourcePath.SHAPE]

        queries = {}
        index_helper_instance = None
        for key, index_helper in zip(key_list, index_helper_list):
            index_helper_instance = index_helper()
            queries[key] = index_helper_instance.get_data_by_file()

        answer = index_helper_instance.make_multisearch_query_for_aggs(queries)

        doc_number_by_file = {}
        for key in answer:
            files = answer[key]['aggregations']['files']['buckets']
            for data_file in files:
                doc_number_by_file[data_file['key']] = data_file['doc_count']

        return doc_number_by_file

    def get(self, request):
        """ expedition data """
        uploaded_files = self.get_uploaded_files()
        file_list = self.get_file_list()

        for key in file_list:
            for data_file in file_list[key]:
                del data_file['path']
                data_file['docNumber'] = uploaded_files[data_file['name']] if data_file['name'] in uploaded_files else 0

        response = {
            'routeDictFiles': file_list
        }

        return JsonResponse(response)
