# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from datamanager.views import LoadManagerHTML, GetLoadFileData, LoadData, DeleteData

app_name = 'datamanager'
urlpatterns = [
    url(r'^loadManager$', login_required(LoadManagerHTML.as_view()), name='loadmanager'),
    url(r'^loadManager/data$', login_required(GetLoadFileData.as_view()), name='getLoadFileData'),
    url(r'^loadData', login_required(LoadData.as_view()), name='loadData'),
    url(r'^deleteData', login_required(DeleteData.as_view()), name='deleteData')
]
