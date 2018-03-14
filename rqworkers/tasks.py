# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_rq import job
from django.conf import settings
from django.utils import timezone

from rq import get_current_job

from rqworkers.dataUploader.loadData import upload_file

from datamanager.models import UploaderJobExecution

import time
import sys


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
    try:
        upload_file(settings.ES_CLIENT, path_to_file)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.status = UploaderJobExecution.FINISHED
        job_execution_obj.save()
    except Exception:
        exc_type, exc_value, traceback = sys.exc_info()
        exception_handler(job_instance, exc_type, exc_value, traceback)


def exception_handler(job_instance, exc_type, exc_value, traceback):
    job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FAILED
    job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, traceback)
    job_execution_obj.save()

    # continue with the next handler if exists, for instance: failed queue
    return True
