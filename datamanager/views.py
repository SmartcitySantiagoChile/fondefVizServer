# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from esapi.errors import GenericError

from rqworkers.dataUploader.errors import IndexNotEmptyError

from datamanager.errors import IndexWithDocumentError, BadFormatDocumentError, ThereIsNotActiveJobError
from datamanager.messages import JobEnqueued, DataDeletedSuccessfully, JobCanceledSuccessfully
from datamanager.helper import UploaderManager, FileManager

from rq.exceptions import NoSuchJobError


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
            }
        ]
        operation_program_tables = [
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
            'tables': tables,
            'operation_program_tables': operation_program_tables
        }

        return render(request, template, context)


class UploadData(View):
    """ Load data to elastic search """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadData, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            UploaderManager(file_name).upload_data()
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

    def post(self, request):
        """  """
        file_name = request.POST.get('fileName', '')

        response = {}
        try:
            deleted_doc_number = UploaderManager(file_name).delete_data()
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
            UploaderManager(file_name).cancel_uploading()
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

    def get(self, request):
        """ expedition data """

        response = {
            'routeDictFiles': FileManager().get_file_list()
        }

        return JsonResponse(response)
