# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q

from datamanager.models import ExporterJobExecution


def export_job(request):
    jobs = ExporterJobExecution.objects.filter(Q(seen=False) | Q(status=ExporterJobExecution.RUNNING),
                                               user=request.user)
    # if there is not running jobs or not seen jobs shows last 3
    if len(jobs) == 0:
        jobs = ExporterJobExecution.objects.filter(user=request.user).order_by('-enqueueTimestamp')[:3]

    return {
        'jobs': jobs
    }
