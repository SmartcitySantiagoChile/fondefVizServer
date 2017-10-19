from django.conf.urls import url
from .views import Show, Data

app_name='globalstat'
urlpatterns = [
  url(r'^show$', Show.as_view(), name='show'),
  url(r'^data$', Data.as_view(), name='data'),
]
