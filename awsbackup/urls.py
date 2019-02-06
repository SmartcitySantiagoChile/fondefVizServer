# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from awsbackup.views import TableHTML, AvailableDays

app_name = 'awsbackup'
urlpatterns = [
    url(r'^gps/$', login_required(TableHTML.as_view()), name='gps'),
    url(r'^trips/$', login_required(TableHTML.as_view()), name='trips'),
    url(r'^opprogram/$', login_required(TableHTML.as_view()), name='opprogram'),

    url(r'^availableDays/$', login_required(AvailableDays.as_view()), name='availableDays'),
]
