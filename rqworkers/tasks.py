# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_rq import job
from django.conf import settings
from django.utils import timezone

from rq import get_current_job

from rqworkers.dataUploader.loadData import upload_file

from datamanager.models import UploaderJobExecution


@job('default')
def upload_file_job(path_to_file, job_execution_obj):
    # update start timestamp
    job_execution_obj.jobId = get_current_job().id
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.save()

    upload_file(settings.ES_CLIENT, path_to_file)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FINISHED
    job_execution_obj.save()


def exception_handler(job, exc_type, exc_value, traceback):
    job_execution_obj = UploaderJobExecution.objects.get(jobId=job.id)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FAILED
    job_execution_obj.errorMessage = str(traceback)

    # continue with the next handler if exists, for instance: failed queue
    return True