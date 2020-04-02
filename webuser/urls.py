# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from webuser.views import PasswordChangeView

app_name = 'webuser'
urlpatterns = [
    url(r'^password_change/$', login_required(PasswordChangeView.as_view()), name='password_change'),
]
