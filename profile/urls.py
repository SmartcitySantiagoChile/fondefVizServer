# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from profile.views.LoadProfileByExpedition import LoadProfileByExpeditionView
from profile.views.LoadProfileByStop import LoadProfileByStopView
from profile.views.ODMatrix import ODMatrixView
from profile.views.Transfers import TransfersView, GetTransfersData
from profile.views.Trajectory import TrajectoryView

app_name = 'profile'
urlpatterns = [
    # html
    url(r'^expedition$', login_required(LoadProfileByExpeditionView.as_view()), name='expedition'),
    url(r'^stop$', login_required(LoadProfileByStopView.as_view()), name='stop'),
    url(r'^trajectory$', login_required(TrajectoryView.as_view()), name='trajectory'),
    url(r'^transfers$', login_required(TransfersView.as_view()), name='transfers'),
    url(r'^odmatrix$', login_required(ODMatrixView.as_view()), name='odmatrix'),
    # data
    url(r'^getTransfersData$', GetTransfersData.as_view(), name="getTransfersData"),
]
