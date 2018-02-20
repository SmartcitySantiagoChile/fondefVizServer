from django.conf.urls import url

from .views.map import MapHTML
from .views.resume import ResumeHTML
from .views.large import (LoadLargeTravelsView, GetLargeTravelsData)
from .views.from_to import (LoadFromToMapsView, GetFromToMapsData)


app_name = 'travel'
urlpatterns = [
  url(r'^$', MapHTML.as_view(), name='map'),  # dafaults to map
  url(r'^map$', MapHTML.as_view(), name='map'),
  url(r'^resume$', ResumeHTML.as_view(), name='graphs'),
  url(r'^large-travels$', LoadLargeTravelsView.as_view(), name='large-travels'),
  url(r'^fromToMaps$', LoadFromToMapsView.as_view(), name='from-to'),
  url(r'^getLargeTravelsData$', GetLargeTravelsData.as_view()),
  url(r'^getFromToMapsData$', GetFromToMapsData.as_view())
]
