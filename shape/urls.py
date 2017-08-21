from django.conf.urls import url
from .views import Route, Map

app_name='shape'
urlpatterns = [
  url(r'^route$', Route.as_view(), name='route'),
  url(r'^map$', Map.as_view(), name='map'),

]
