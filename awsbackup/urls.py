# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from awsbackup.views import TableHTML, AvailableDays, AWSSession

app_name = 'awsbackup'
urlpatterns = [
    url(r'^gps/$', login_required(TableHTML.as_view(bucket_name=AWSSession.GPS_BUCKET_NAME, subtitle='GPS')),
        name='gps'),
    url(r'^trips/$', login_required(TableHTML.as_view(bucket_name=AWSSession.TRIP_BUCKET_NAME, subtitle='Viajes')),
        name='trips'),
    url(r'^opprogram/$',
        login_required(TableHTML.as_view(bucket_name=AWSSession.OP_PROGRAM_BUCKET_NAME, subtitle='Programa de operación')),
        name='opprogram'),

    url(r'^availableDays/(?P<bucket_name>[\w-]+)/$', login_required(AvailableDays.as_view()), name='availableDays'),
]
