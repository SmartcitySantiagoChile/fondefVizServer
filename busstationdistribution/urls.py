# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from busstationdistribution.views import IndexHTML

app_name = 'busstationdistribution'
urlpatterns = [
    # html
    url(r'^$', login_required(IndexHTML.as_view()), name='index'),
]
