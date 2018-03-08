# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from collections import defaultdict
from itertools import groupby

from esapi.helper.profile import ESProfileHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.resume import ESResumeStatisticHelper

from datamanager.errors import FileDoesNotExist, ThereIsPreviousJobUploadingTheFile
from datamanager.models import DataSourcePath, LoadFile, UploaderJobExecution

from rqworkers.tasks import upload_file_job

import os
import glob


class LoadData(View):
    """ Load data to elastic search """

    def post(self, request):
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            if LoadFile.objects.filter(fileName=file_name).exists():
                file_path_obj = LoadFile.objects.get(fileName=file_name)
            else:
                raise FileDoesNotExist()

            if True:
                # check if exist job associate to file obj
                pass
            else:
                raise ThereIsPreviousJobUploadingTheFile()

            job_execution_obj = UploaderJobExecution.objects.create(enqueueTimestamp=timezone.now(),
                                                                    status=UploaderJobExecution.ENQUEUED,
                                                                    file=file_path_obj)
            file_path = os.path.join(file_path_obj.path, file_name)
            upload_file_job.delay(file_path, job_execution_obj)

            response['status'] = {
                'code': 200,
                'message': 'El archivo ha sido encolado para ser subido, esto puede tomar tiempo. Paciencia :-)',
                'title': 'Datos eliminados',
                'type': 'info'
            }
        except FileDoesNotExist as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class DeleteData(View):
    """ Delete data from elastic search """

    def post(self, request):
        """  """
        index = request.POST.get('index', '')
        file_name = request.POST.get('fileName', '')

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

        index_helper().delete_data_by_file(file_name)

        response = {
            'status': {
                'code': 200,
                'message': 'Los datos fueron eliminados correctamente.',
                'title': 'Datos eliminados',
                'type': 'info'
            }
        }

        return JsonResponse(response)


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


class GetLoadFileData(View):
    """ """

    def count_doc_in_file(self, data_source, file_path):
        i = 0
        if data_source.code in [DataSourcePath.SHAPE, DataSourcePath.STOP]:
            with open(file_path) as f:
                i = len(list(groupby(f, lambda row: row.split(str('|'))[0])))
            # not count header
            i -= 1
        else:
            # how it starts from zero is not count header
            with open(file_path) as f:
                for i, _ in enumerate(f):
                    pass

        return i

    def get_file_list(self):
        """ list all files in directory with code """
        file_dict = defaultdict(list)

        for data_source in DataSourcePath.objects.all():
            path = data_source.path
            # if is running on windows
            if os.name == 'nt':
                path = os.path.join(settings.BASE_DIR, 'media')

            path_name = os.path.join(path, data_source.filePattern)
            file_name_list = glob.glob(path_name)

            for file_path in file_name_list:
                file_name = os.path.basename(file_path)
                file_obj, created = LoadFile.objects.get_or_create(fileName=file_name, defaults={
                    'dataSourcePath': path,
                    'discoverAt': timezone.now()
                })
                if created:
                    file_obj.lines = self.count_doc_in_file(data_source, file_path)
                else:
                    file_obj.dataSourcePath = path
                file_obj.save()
                file_dict[data_source.code].append(file_obj.get_dict())

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
