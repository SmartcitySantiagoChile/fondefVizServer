from django.conf.urls import url
from .views import ResumeHTML, DetailHTML

app_name = 'globalstat'
urlpatterns = [
    url(r'^resume$', ResumeHTML.as_view(), name='resume'),
    url(r'^detail$', DetailHTML.as_view(), name='detail'),
]
