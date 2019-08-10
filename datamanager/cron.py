# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from datamanager.models import ExporterJobExecution

import os


def delete_old_file_job():
    """
    Delete old files
    :return: None
    """
    thirty_day_less = timezone.now() - timezone.timedelta(days=30)

    jobs = ExporterJobExecution.objects.filter(enqueueTimestamp__lte=thirty_day_less)

    for job in jobs:
        job.status = ExporterJobExecution.EXPIRED
        if bool(job.file):
            if os.path.isfile(job.file.path):
                os.remove(job.file.path)
