# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shape.views import MapHTML

app_name = 'shape'
urlpatterns = [
    url(r'^map/$', login_required(MapHTML.as_view()), name='map'),
]
