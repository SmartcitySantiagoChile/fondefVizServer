from django.conf.urls import url
from .views import Resume, Data, Detail

app_name='globalstat'
urlpatterns = [
  url(r'^resume$', Resume.as_view(), name='resume'),
  url(r'^data$', Data.as_view(), name='data'),
  url(r'^detail$', Detail.as_view(), name='detail'),
]
