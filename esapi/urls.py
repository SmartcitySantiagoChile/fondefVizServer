# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from esapi.views.profile import MatchedStopData, LoadProfileByStopData, AvailableDays, AvailableRoutes, \
    LoadProfileByExpeditionData
from esapi.views.odbyroute import AvailableDays as ODAD, AvailableRoutes as ODAR, ODMatrixData
from esapi.views.resume import GlobalData, AvailableDays as StatisticAD
from esapi.views.speed import AvailableDays as SAD, AvailableRoutes as SAR, MatrixData, RankingData, SpeedByRoute, \
    SpeedVariation
from esapi.views.travel import ResumeData, AvailableDays as TAD, MapData, LargeTravelData, FromToMapData, StrategiesData

app_name = 'esapi'
urlpatterns = [
    # profile index
    url(r'^profile/matchedStopData$', login_required(MatchedStopData.as_view()), name='matchedStopData'),
    url(r'^profile/loadProfileByStopData$', login_required(LoadProfileByStopData.as_view()),
        name='loadProfileByStopData'),
    url(r'^profile/loadProfileByExpeditionData$', login_required(LoadProfileByExpeditionData.as_view()),
        name='loadProfileByExpeditionData'),
    url(r'^profile/availableDays$', login_required(AvailableDays.as_view()), name='availableProfileDays'),
    url(r'^profile/availableRoutes$', login_required(AvailableRoutes.as_view()), name='availableProfileRoutes'),

    # odbyroute index
    url(r'^odbyroute/matrixData$', login_required(ODMatrixData.as_view()), name='ODMatrixData'),
    url(r'^odbyroute/availableDays$', login_required(ODAD.as_view()), name='availableODDays'),
    url(r'^odbyroute/availableRoutes$', login_required(ODAR.as_view()), name='availableODRoutes'),

    # general index
    url(r'^resume/data$', login_required(GlobalData.as_view()), name='resumeData'),
    url(r'^resume/availableDays$', login_required(StatisticAD.as_view()), name='availableStatisticDays'),

    # speed index
    url(r'^speed/availableDays$', login_required(SAD.as_view()), name='availableSpeedDays'),
    url(r'^speed/availableRoutes$', login_required(SAR.as_view()), name='availableSpeedRoutes'),
    url(r'^speed/matrixData$', login_required(MatrixData.as_view()), name='matrixData'),
    url(r'^speed/rankingData$', login_required(RankingData.as_view()), name='rankingData'),
    url(r'^speed/speedByRoute$', login_required(SpeedByRoute.as_view()), name='speedByRoute'),
    url(r'^speed/speedVariation$', login_required(SpeedVariation.as_view()), name='speedVariation'),

    # trip index
    url(r'^trip/resumeData', login_required(ResumeData.as_view()), name='resumeTripData'),
    url(r'^trip/largeTravelData', login_required(LargeTravelData.as_view()), name='largeTravelData'),
    url(r'^trip/fromToMapData', login_required(FromToMapData.as_view()), name='fromToMapData'),
    url(r'^trip/strategiesData', login_required(StrategiesData.as_view()), name='tripStrategiesData'),
    url(r'^trip/mapData', login_required(MapData.as_view()), name='tripMapData'),
    url(r'^trip/availableDays', login_required(TAD.as_view()), name='availableTripDays'),

    # shape index
    # url(r'^shape', login_required(DeleteData.as_view()), name='deleteData'),
]
