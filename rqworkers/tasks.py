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

from datamanager.models import UploaderJobExecution, ExporterJobExecution

import time
import uuid
import os


@job('data_uploader')
def upload_file_job(path_to_file):
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

    upload_file(settings.ES_CLIENT, path_to_file)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FINISHED
    job_execution_obj.save()


def upload_exception_handler(job_instance, exc_type, exc_value, traceback):
    try:
        job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, traceback)
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
        subject = 'Los datos se encuentran disponibles'
        body = """
        Los datos que ha solicitado están disponibles en la siguiente dirección:
        
        {0}
        
        El link estará disponible por 30 días, luego de eso tendrá que volver a generar la consulta.
        
        Saludos
        """.format(job_execution_obj.file.url)
        sender = 'noreply@transapp.cl'
        send_mail(subject, body, sender, [job_execution_obj.user.email])

        job_execution_obj.status = ExporterJobExecution.FINISHED
    except SMTPException as e:
        job_execution_obj.status = ExporterJobExecution.FINISHED_BUT_MAIL_WAS_NOT_SENT
        job_execution_obj.errorMessage = str(e)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()


def export_exception_handler(job_instance, exc_type, exc_value, traceback):
    try:
        job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.seen = False
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, traceback)
        job_execution_obj.save()
    except ExporterJobExecution.DoesNotExist:
        pass

    # continue with the next handler if exists, for instance: failed queue
    return True
