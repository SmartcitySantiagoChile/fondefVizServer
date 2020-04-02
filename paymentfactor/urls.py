# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from paymentfactor.views import IndexHTML

app_name = 'paymentfactor'
urlpatterns = [
    # html
    url(r'^$', login_required(IndexHTML.as_view()), name='index'),
]
