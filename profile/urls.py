# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from profile.views import LoadProfileByExpeditionHTML, LoadProfileByStopHTML, ODMatrixHTML, TrajectoryHTML
from profile.views2.Transfers import TransfersView, GetTransfersData

app_name = 'profile'
urlpatterns = [
    # html
    url(r'^expedition/$', login_required(LoadProfileByExpeditionHTML.as_view()), name='expedition'),
    url(r'^stop/$', login_required(LoadProfileByStopHTML.as_view()), name='stop'),
    url(r'^trajectory/$', login_required(TrajectoryHTML.as_view()), name='trajectory'),
    url(r'^transfers/$', login_required(TransfersView.as_view()), name='transfers'),
    url(r'^odmatrix/$', login_required(ODMatrixHTML.as_view()), name='odmatrix'),
    # data
    url(r'^getTransfersData/$', GetTransfersData.as_view(), name="getTransfersData"),
]
