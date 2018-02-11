# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from esapi.views.profile import MatchedStopData, LoadProfileByStopData, AvailableDays, AvailableRoutes, \
    LoadProfileByExpeditionData
from esapi.views.odbyroute import AvailableDays as ODAD, AvailableRoutes as ODAR, ODMatrixData

app_name = "esapi"
urlpatterns = [
    # profile index
    url(r'^profile/matchedStopData$', login_required(MatchedStopData.as_view()), name="matchedStopData"),
    url(r'^profile/loadProfileByStopData$', login_required(LoadProfileByStopData.as_view()),
        name="loadProfileByStopData"),
    url(r'^profile/loadProfileByExpeditionData$', login_required(LoadProfileByExpeditionData.as_view()),
        name="loadProfileByExpeditionData"),
    url(r'^profile/availableDays$', login_required(AvailableDays.as_view()), name="availableProfileDays"),
    url(r'^profile/availableRoutes$', login_required(AvailableRoutes.as_view()), name="availableProfileRoutes"),

    # odbyroute index
    url(r'^odbyroute/matrixData$', login_required(ODMatrixData.as_view()), name="ODMatrixData"),
    url(r'^odbyroute/availableDays$', login_required(ODAD.as_view()), name="availableODDays"),
    url(r'^odbyroute/availableRoutes$', login_required(ODAR.as_view()), name="availableODRoutes"),

    # speed index
    url(r'^speed$', login_required(getLoadFileData.as_view()), name="getloadfiledata"),

    # trip index
    url(r'^trip', login_required(LoadData.as_view()), name="loadData"),

    # shape index
    url(r'^shape', login_required(DeleteData.as_view()), name="deleteData"),
]
