# -*- coding: utf-8 -*-


from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from localinfo.views import TimePeriod, OPDictionaryCsvUploader, FaqImgUploader, FaqHTML

app_name = 'localinfo'
urlpatterns = [
    url(r'^timePeriod/$', login_required(TimePeriod.as_view()), name='timePeriod'),
    url(r'^csvuploadOP/$', login_required(OPDictionaryCsvUploader.as_view()),
        name='opdictionarycsvupload'),
    url(r'^faqUpload/$', login_required(FaqImgUploader.as_view()), name='faqUpload'),
    url(r'^faq/$', FaqHTML.as_view(), name='faq'),
]
