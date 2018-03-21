# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_rq import job
from django.conf import settings
from django.utils import timezone

from elasticsearch_dsl import Search

from rq import get_current_job

from rqworkers.dataUploader.loadData import upload_file
from rqworkers.dataDownloader.downloadData import download_file

from datamanager.models import UploaderJobExecution, ExporterJobExecution

import time
import os
import json


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
def export_data_job(es_query_dict, index_name):
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
    job_execution_obj.save()

    file_name = "data_query.zip"
    csv_file = os.path.join(settings.BASE_DIR, 'media', 'files', file_name)
    download_file(settings.ES_CLIENT, json.dumps(es_query_dict), index_name, csv_file)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = ExporterJobExecution.FINISHED
    job_execution_obj.save()


def export_exception_handler(job_instance, exc_type, exc_value, traceback):
    try:
        job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, traceback)
        job_execution_obj.save()
    except ExporterJobExecution.DoesNotExist:
        pass

    # continue with the next handler if exists, for instance: failed queue
    return True
