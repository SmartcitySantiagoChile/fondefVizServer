from django.conf.urls import url
from .views import Resume, Detail

app_name='globalstat'
urlpatterns = [
  url(r'^resume$', Resume.as_view(), name='resume'),
  url(r'^detail$', Detail.as_view(), name='detail'),
]
