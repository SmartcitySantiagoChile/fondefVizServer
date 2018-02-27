# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import LoadManager, getLoadFileData, LoadData, DeleteData

app_name = 'datamanager'
urlpatterns = [
    url(r'^loadManager$', login_required(LoadManager.as_view()), name='loadmanager'),
    url(r'^loadManager/data$', login_required(getLoadFileData.as_view()), name='getLoadFileData'),
    url(r'^loadData', login_required(LoadData.as_view()), name='loadData'),
    url(r'^deleteData', login_required(DeleteData.as_view()), name='deleteData')
]
