from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from localinfo.views import TimePeriod, OPDictionaryUploader, FaqImgUploader, FaqHTML, OPProgramList, DownloadUserList

app_name = 'localinfo'
urlpatterns = [
    url(r'^timePeriod/$', login_required(TimePeriod.as_view()), name='timePeriod'),
    url(r'^uploadOP/$', staff_member_required(OPDictionaryUploader.as_view()),
        name='opdictionaryupload'),
    url(r'^faqUpload/$', staff_member_required(FaqImgUploader.as_view()), name='faqUpload'),
    url(r'^faq/$', login_required(FaqHTML.as_view()), name='faq'),
    url(r'^opProgramList/$', login_required(OPProgramList.as_view()), name='opProgramList'),
    url(r'^downloadUserData/$', staff_member_required(DownloadUserList.as_view()), name='downloaduserlist')

]
