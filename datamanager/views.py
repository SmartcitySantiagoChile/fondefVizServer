# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q

from esapi.errors import FondefVizError

from rqworkers.dataUploader.errors import IndexNotEmptyError

from datamanager.errors import IndexWithDocumentError, BadFormatDocumentError, ThereIsNotActiveJobError
from datamanager.messages import JobEnqueued, DataDeletedSuccessfully, JobCanceledSuccessfully, DataIsDeleting
from datamanager.helper import UploaderManager, FileManager
from datamanager.models import LoadFile, UploaderJobExecution

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
            data_file = UploaderManager(file_name).upload_data().get_dictionary()
            doc_number_by_file = FileManager().get_document_number_by_file_from_elasticsearch(file_name)
            data_file['docNumber'] = doc_number_by_file[file_name] if file_name in doc_number_by_file else 0

            response['data'] = data_file
            response['status'] = JobEnqueued().get_status_response()
        except FondefVizError as e:
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
            response['data'] = {
                'deletedDocNumber': deleted_doc_number
            }
            if deleted_doc_number is None:
                response['status'] = DataIsDeleting().get_status_response()
            else:
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
            data_file = UploaderManager(file_name).cancel_uploading().get_dictionary()
            doc_number_by_file = FileManager().get_document_number_by_file_from_elasticsearch(file_name)
            data_file['docNumber'] = doc_number_by_file[file_name] if file_name in doc_number_by_file else 0

            response['data'] = data_file
            response['status'] = JobCanceledSuccessfully().get_status_response()
        except FondefVizError as e:
            response['status'] = e.get_status_response()
        except NoSuchJobError:
            response['status'] = ThereIsNotActiveJobError().get_status_response()
        except IndexError:
            response['status'] = BadFormatDocumentError().get_status_response()

        return JsonResponse(response)


class LatestJobChanges(View):
    """ return list of files which change last x minutes """

    def get(self, request):
        minutes = 2
        lower_time_bound = timezone.now() - timezone.timedelta(minutes=minutes)

        files = LoadFile.objects.filter(Q(uploaderjobexecution__executionStart__gte=lower_time_bound) | Q(
            uploaderjobexecution__executionEnd__gte=lower_time_bound) | Q(
            uploaderjobexecution__status=UploaderJobExecution.RUNNING))

        filter_list = map(lambda x: x.fileName, files)
        doc_number_by_file = FileManager().get_document_number_by_file_from_elasticsearch(filter_list)

        changes = []
        for data_file in files:
            file_name = data_file.fileName
            data_file = data_file.get_dictionary()
            data_file['docNumber'] = doc_number_by_file[file_name] if file_name in doc_number_by_file else 0
            changes.append(data_file)

        response = {
            'changes': changes
        }

        return JsonResponse(response)


class GetLoadFileData(View):
    """ """

    def get(self, request):
        """ expedition data """

        response = {
            'routeDictFiles': FileManager().get_file_list()
        }

        return JsonResponse(response)
