# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from profile.views import LoadProfileByExpeditionHTML, LoadProfileByStopHTML, ODMatrixHTML, TrajectoryHTML, \
    TransfersView, LoadProfileByManyStopsHTML

app_name = 'profile'
urlpatterns = [
    # html
    url(r'^expedition/$', login_required(LoadProfileByExpeditionHTML.as_view()), name='expedition'),
    url(r'^stop/$', login_required(LoadProfileByStopHTML.as_view()), name='stop'),
    url(r'^trajectory/$', login_required(TrajectoryHTML.as_view()), name='trajectory'),
    url(r'^transfers/$', login_required(TransfersView.as_view()), name='transfers'),
    url(r'^odmatrix/$', login_required(ODMatrixHTML.as_view()), name='odmatrix'),
    url(r'^manystops/$', login_required(LoadProfileByManyStopsHTML.as_view()), name='manystops'),
]
