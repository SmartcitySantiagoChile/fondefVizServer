# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shape.views import GetBaseInfo, GetRouteInfo, MapHTML

app_name = 'shape'
urlpatterns = [
    url(r'^route/$', login_required(GetRouteInfo.as_view()), name='route'),
    url(r'^base/$', login_required(GetBaseInfo.as_view()), name='base'),
    url(r'^map/$', login_required(MapHTML.as_view()), name='map'),
]
