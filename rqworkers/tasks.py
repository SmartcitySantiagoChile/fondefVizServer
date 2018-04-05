# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_rq import job
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.core.files import File

from smtplib import SMTPException

from rq import get_current_job

from rqworkers.dataUploader.loadData import upload_file
from rqworkers.dataDownloader.downloadData import download_file

from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper

from datamanager.models import UploaderJobExecution, ExporterJobExecution

from itertools import groupby

import time
import uuid
import os
import zipfile
import io
import traceback


@job('data_uploader')
def upload_file_job(path_to_file, index_name_list):
    job_instance = get_current_job()
    # wait until UploaderJobExecution instance exists
    while True:
        try:
            job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)
            break
        except UploaderJobExecution.DoesNotExist:
            time.sleep(1)

    job_execution_obj.status = UploaderJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.save()

    for index_name in index_name_list:
        upload_file(settings.ES_CLIENT, path_to_file, index_name)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FINISHED
    job_execution_obj.save()


def upload_exception_handler(job_instance, exc_type, exc_value, exc_tb):
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, tb_str)
        job_execution_obj.save()
    except UploaderJobExecution.DoesNotExist:
        pass
    # continue with the next handler if exists, for instance: failed queue
    return True


@job('data_exporter')
def export_data_job(es_query_dict, downloader):
    job_instance = get_current_job()
    # wait until ExporterJobExecution instance exists
    while True:
        try:
            job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)
            break
        except ExporterJobExecution.DoesNotExist:
            time.sleep(1)

    job_execution_obj.status = ExporterJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()

    file_name = "{0}.zip".format(uuid.uuid4())
    zip_file = os.path.join(settings.DOWNLOAD_PATH, file_name)
    download_file(settings.ES_CLIENT, es_query_dict, downloader, zip_file)

    # update file path
    job_execution_obj.file.save(file_name, File(open(zip_file)))

    try:
        subject = 'Los datos solicitados ya se encuentran disponibles'
        body = """
        Hola
        
        Los datos que ha solicitado ya están disponibles en la platafora. Para acceder a ellos siga los siguientes pasos: 
        
        - Ingrese a la plataforma
        - En la sección superior derecha seleccione su nombre de ususario, se desplegará un menú
        - En el menú presionar "Solicitudes de descarga"
        - En este punto encontrará una lista con todas las solicitudes de datos ordenadas por antiguedad
        
        Recuerde que el archivo estará disponible por 30 días, luego de eso tendrá que volver a generar la consulta.
        
        Saludos
        """
        sender = 'noreply@transapp.cl'
        send_mail(subject, body, sender, [job_execution_obj.user.email])

        job_execution_obj.status = ExporterJobExecution.FINISHED
    except SMTPException as e:
        job_execution_obj.status = ExporterJobExecution.FINISHED_BUT_MAIL_WAS_NOT_SENT
        job_execution_obj.errorMessage = str(e)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()


def export_exception_handler(job_instance, exc_type, exc_value, exc_tb):
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.seen = False
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, tb_str)
        job_execution_obj.save()
    except ExporterJobExecution.DoesNotExist:
        pass

    # continue with the next handler if exists, for instance: failed queue
    return True


@job('count_lines')
def count_line_of_file_job(file_obj, data_source_code, file_path):
    def get_file_object(_file_path):
        """
        :param _file_path: file path will upload
        :return: file object
        """
        if zipfile.is_zipfile(_file_path):
            zip_file_obj = zipfile.ZipFile(_file_path, 'r')
            # it assumes that zip file has only one file
            file_name = zip_file_obj.namelist()[0]
            _file_obj = zip_file_obj.open(file_name, 'rU')
        else:
            _file_obj = io.open(_file_path, str('rb'))

        return _file_obj

    i = 0
    with get_file_object(file_path) as f:
        if data_source_code in [ESShapeHelper().index_name, ESStopByRouteHelper().index_name]:
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

    file_obj.refresh_from_db()
    file_obj.lines = i
    file_obj.save()
