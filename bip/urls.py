# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from bip.views import LoadBipByOperatorHTML
app_name = 'bip'
urlpatterns = [
    # html
    url(r'^operator/$', login_required(LoadBipByOperatorHTML.as_view()), name='operator'),
]
