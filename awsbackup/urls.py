# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from awsbackup.views import TableHTML, AvailableDays
from awsbackup.aws import AWSSession

app_name = 'awsbackup'

params = [
    dict(bucket_name=AWSSession.GPS_BUCKET_NAME, subtitle='GPS'),
    dict(bucket_name=AWSSession.TRIP_BUCKET_NAME, subtitle='viajes'),
    dict(bucket_name=AWSSession.OP_PROGRAM_BUCKET_NAME, subtitle='Programas de operación'),
    dict(bucket_name=AWSSession.REPRESENTATIVE_WEEk_BUCKET_NAME, subtitle='Semanas representativas'),
    dict(bucket_name=AWSSession.FILE_196_BUCKET_NAME, subtitle='Reportes 1.96'),
    dict(bucket_name=AWSSession.PROFILE_BUCKET_NAME, subtitle='Perfiles'),
    dict(bucket_name=AWSSession.STAGE_BUCKET_NAME, subtitle='Etapas'),
    dict(bucket_name=AWSSession.SPEED_BUCKET_NAME, subtitle='Velocidades'),
    dict(bucket_name=AWSSession.TRANSACTION_BUCKET_NAME, subtitle='Transacciones'),
]
urlpatterns = [
    url(r'^gps/$', login_required(TableHTML.as_view(**params[0])), name='gps'),
    url(r'^trip/$', login_required(TableHTML.as_view(**params[1])), name='trip'),
    url(r'^opprogram/$', login_required(TableHTML.as_view(**params[2])), name='opprogram'),
    url(r'^representativeweek/$', login_required(TableHTML.as_view(**params[3])), name='representativeweek'),
    url(r'^196/$', login_required(TableHTML.as_view(**params[4])), name='196'),
    url(r'^profile/$', login_required(TableHTML.as_view(**params[5])), name='profile'),
    url(r'^stage/$', login_required(TableHTML.as_view(**params[6])), name='stage'),
    url(r'^speed/$', login_required(TableHTML.as_view(**params[7])), name='speed'),
    url(r'^transaction/$', login_required(TableHTML.as_view(**params[8])), name='transaction'),

    url(r'^availableDays/(?P<bucket_name>[\w-]+)/$', login_required(AvailableDays.as_view()), name='availableDays'),
]
