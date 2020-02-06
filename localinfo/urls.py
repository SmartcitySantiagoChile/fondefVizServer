# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from views import FaqImgUploader, FaqHTML

app_name = 'localinfo'
urlpatterns = [
    url(r'^faqUpload/$', login_required(FaqImgUploader.as_view()), name='faqUpload'),
    url(r'^faq/$', FaqHTML.as_view(), name='faq'),
]
