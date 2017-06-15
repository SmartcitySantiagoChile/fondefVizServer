from django.conf.urls import url
from .views import common

app_name='indicators'
urlpatterns = [
  url(r'^$', common.index, name='index'),
]
