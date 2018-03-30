# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from trip.views import MapHTML, ResumeHTML, LargeTripsHTML, FromToMapHTML, TripStrategiesHTML

app_name = 'trip'
urlpatterns = [
    url(r'^$', login_required(MapHTML.as_view()), name='map'),  # dafaults to map
    url(r'^map/$', login_required(MapHTML.as_view()), name='map'),
    url(r'^resume/$', login_required(ResumeHTML.as_view()), name='graphs'),
    url(r'^strategies/$', login_required(TripStrategiesHTML.as_view()), name='strategies'),
    url(r'^large-trips/$', login_required(LargeTripsHTML.as_view()), name='large-trips'),
    url(r'^fromToMaps/$', login_required(FromToMapHTML.as_view()), name='from-to')
]
