# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import ResumeHTML, DetailHTML

app_name = 'globalstat'
urlpatterns = [
    url(r'^resume/$', login_required(ResumeHTML.as_view()), name='resume'),
    url(r'^detail/$', login_required(DetailHTML.as_view()), name='detail'),
]
