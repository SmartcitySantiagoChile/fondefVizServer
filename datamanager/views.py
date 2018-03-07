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

from datamanager.models import DataSourcePath, DataSourceFile

from rqworkers.tasks import test_func

import os
import re


class TestTask(View):

    def get(self, request):
        # enqueue
        job = test_func.delay(1, 2)
        print(a)
        print(type(a))

        return JsonResponse({'status': 'wena'})


class LoadData(View):
    """ Load data to elastic search """

    def __init__(self):
        self.context = {}

    def post(self, request):
        """  """


class DeleteData(View):
    """ Delete data from elastic search """

    def __init__(self):
        self.context = {}

    def post(self, request):
        """  """


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


class getLoadFileData(View):
    """ """

    def count_doc_in_file(self, data_source, path, file_name):
        i = 0
        if data_source.code in [DataSourcePath.SHAPE, DataSourcePath.STOP]:
            with open(os.path.join(path, file_name)) as f:
                i = len(list(groupby(f, lambda row: row.split(str('|'))[0])))
            # not count header
            i -= 1
        else:
            # how it starts from zero is not count header
            with open(os.path.join(path, file_name)) as f:
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

            pattern = re.compile('.{}$'.format(data_source.filePattern))
            file_name_list = filter(lambda fileName: pattern.match(fileName), os.listdir(path))
            for file_name in file_name_list:
                file_obj, created = DataSourceFile.objects.get_or_create(fileName=file_name, defaults={
                    'dataSourcePath': path,
                    'discoverAt': timezone.now()
                })
                if not created:
                    file_obj.lines = self.count_doc_in_file(data_source, path, file_name)
                    file_obj.save()
                file_dict[data_source.code].append(file_obj.getDict())

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
            for file in files:
                doc_number_by_file[file['key']] = file['doc_count']

        return doc_number_by_file

    def get(self, request):
        """ expedition data """
        uploaded_files = self.get_uploaded_files()
        file_list = self.get_file_list()

        for key in file_list:
            for file in file_list[key]:
                del file['path']
                file['docNumber'] = uploaded_files[file['name']] if file['name'] in uploaded_files else 0

        response = {
            'routeDictFiles': file_list
        }

        return JsonResponse(response, safe=False)
