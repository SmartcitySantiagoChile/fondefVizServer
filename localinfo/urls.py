# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from localinfo.views import CalendarInfo

app_name = 'localinfo'
urlpatterns = [
    url(r'^calendarInfo/$', login_required(CalendarInfo.as_view()), name="calendarInfo"),
]
