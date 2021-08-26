from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from localinfo.views import TimePeriod, OPDictionaryUploader, FaqImgUploader, FaqHTML, OPProgramList, DownloadUserList

app_name = 'localinfo'
urlpatterns = [
    url(r'^timePeriod/$', login_required(TimePeriod.as_view()), name='timePeriod'),
    url(r'^uploadOP/$', login_required(OPDictionaryUploader.as_view()),
        name='opdictionaryupload'),
    url(r'^faqUpload/$', login_required(FaqImgUploader.as_view()), name='faqUpload'),
    url(r'^faq/$', login_required(FaqHTML.as_view()), name='faq'),
    url(r'^opProgramList/$', login_required(OPProgramList.as_view()), name='opProgramList'),
    url(r'^downloadUserData/$', login_required(DownloadUserList.as_view()), name='downloaduserlist')

]
