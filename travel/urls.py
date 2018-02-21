# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from travel.views.map import MapHTML
from travel.views.resume import ResumeHTML
from travel.views.large import LargeTravelsHTML
from travel.views.from_to import FromToMapHTML
from travel.views.strategies import TripStrategiesHTML

app_name = 'travel'
urlpatterns = [
    url(r'^$', login_required(MapHTML.as_view()), name='map'),  # dafaults to map
    url(r'^map$', login_required(MapHTML.as_view()), name='map'),
    url(r'^resume$', login_required(ResumeHTML.as_view()), name='graphs'),
    url(r'^strategies$', login_required(TripStrategiesHTML.as_view()), name='strategies'),
    url(r'^large-travels$', login_required(LargeTravelsHTML.as_view()), name='large-travels'),
    url(r'^fromToMaps$', login_required(FromToMapHTML.as_view()), name='from-to')
]
