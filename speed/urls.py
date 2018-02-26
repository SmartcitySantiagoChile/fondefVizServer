# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from speed.views import MatrixHTML, RankingHTML, SpeedVariationHTML

app_name = 'speed'
urlpatterns = [
    # html
    url(r'^matrix$', login_required(MatrixHTML.as_view()), name='matrix'),
    url(r'^ranking$', login_required(RankingHTML.as_view()), name='ranking'),
    url(r'^variation$', login_required(SpeedVariationHTML.as_view()), name='variation')
]
