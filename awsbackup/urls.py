# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from awsbackup.aws import AWSSession
from awsbackup.views import TableHTML, AvailableDays, CreateDownloadLink, ListDownloadLink, TableWithoutCalendarHTML

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
    dict(bucket_name=AWSSession.OP_SPEED_BUCKET_NAME, subtitle='Velocidasdes PO'),
    dict(bucket_name=AWSSession.EARLY_TRANSACTION_BUCKET_NAME, subtitle='Subidas por parada'),
    dict(bucket_name=AWSSession.STOP_TIMES_BUCKET_NAME, subtitle='Cruce buses por paraderos')
]
urlpatterns = [
    url(r'^gps/$', login_required(TableHTML.as_view(**params[0])), name='gps'),
    url(r'^trip/$', login_required(TableHTML.as_view(**params[1])), name='trip'),
    url(r'^opprogram/$', login_required(TableWithoutCalendarHTML.as_view(**params[2])), name='opprogram'),
    url(r'^representativeweek/$', login_required(TableWithoutCalendarHTML.as_view(**params[3])),
        name='representativeweek'),
    url(r'^196/$', login_required(TableHTML.as_view(**params[4])), name='196'),
    url(r'^profile/$', login_required(TableHTML.as_view(**params[5])), name='profile'),
    url(r'^stage/$', login_required(TableHTML.as_view(**params[6])), name='stage'),
    url(r'^speed/$', login_required(TableHTML.as_view(**params[7])), name='speed'),
    url(r'^transaction/$', login_required(TableHTML.as_view(**params[8])), name='transaction'),
    url(r'^opspeed/$', login_required(TableWithoutCalendarHTML.as_view(**params[9])),
        name='opspeed'),
    url(r'earlyTransaction', login_required(TableHTML.as_view(**params[10])), name='early-transaction'),
    url(r'^stoptime/$', login_required(TableHTML.as_view(**params[11])),
        name='stoptime'),
    url(r'^availableDays/(?P<bucket_name>[\w-]+)/$', login_required(AvailableDays.as_view()), name='availableDays'),
    url(r'^createDownloadLink/$', login_required(CreateDownloadLink.as_view()), name='createDownloadLink'),
    url(r'^activeDownloadLink/$', login_required(ListDownloadLink.as_view()), name='activeDownloadLink'),
]
