from django.conf.urls import url
from .views import Show, Data, Detail

app_name='globalstat'
urlpatterns = [
  url(r'^show$', Show.as_view(), name='show'),
  url(r'^data$', Data.as_view(), name='data'),
  url(r'^detail$', Detail.as_view(), name='detail'),
]
