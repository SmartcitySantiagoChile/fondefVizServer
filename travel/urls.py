# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.map import MapHTML
from .views.resume import ResumeHTML
from .views.large import (LoadLargeTravelsView, GetLargeTravelsData)
from .views.from_to import (LoadFromToMapsView, GetFromToMapsData)
from .views.strategies import (LoadStrategiesView, GetStrategiesData)

app_name = 'travel'
urlpatterns = [
    url(r'^$', login_required(MapHTML.as_view()), name='map'),  # dafaults to map
    url(r'^map$', login_required(MapHTML.as_view()), name='map'),
    url(r'^resume$', login_required(ResumeHTML.as_view()), name='graphs'),
    url(r'^strategies$', login_required(LoadStrategiesView.as_view()), name='strategies'),
    url(r'^large-travels$', login_required(LoadLargeTravelsView.as_view()), name='large-travels'),
    url(r'^fromToMaps$', login_required(LoadFromToMapsView.as_view()), name='from-to'),
    url(r'^getLargeTravelsData$', login_required(GetLargeTravelsData.as_view())),
    url(r'^getFromToMapsData$', login_required(GetFromToMapsData.as_view())),
    url(r'^getStrategiesData$', login_required(GetStrategiesData.as_view()))
]
