# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from datamanager.views import LoadManagerHTML, GetLoadFileData, UploadData, DeleteData, CancelData, LatestJobChanges, \
    ExportJobHistoryHTML

app_name = 'datamanager'
urlpatterns = [
    url(r'^manager/$', staff_member_required(LoadManagerHTML.as_view()), name='loadmanager'),
    url(r'^data/$', staff_member_required(GetLoadFileData.as_view()), name='getLoadFileData'),
    url(r'^uploadData/$', staff_member_required(UploadData.as_view()), name='uploadData'),
    url(r'^deleteData/$', staff_member_required(DeleteData.as_view()), name='deleteData'),
    url(r'^cancelData/$', staff_member_required(CancelData.as_view()), name='cancelData'),
    url(r'^latestJobChanges/$', staff_member_required(LatestJobChanges.as_view()), name='latestJobChanges'),
    url(r'^exportJobHistory/$', login_required(ExportJobHistoryHTML.as_view()), name='jobHistoryByUser')
]
