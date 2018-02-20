# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shape.views import Route, Map

app_name = 'shape'
urlpatterns = [
    url(r'^route$', login_required(Route.as_view()), name='route'),
    url(r'^map$', login_required(Map.as_view()), name='map'),

]
