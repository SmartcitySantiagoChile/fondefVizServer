from django.conf.urls import url

from .views.map import (LoadMapView, GetMapData)
from .views.graphs import (LoadGraphsView, GetGraphsData)
from .views.large import (LoadLargeTravelsView, GetLargeTravelsData)
from .views.from_to import (LoadFromToMapsView, GetFromToMapsData)


app_name = 'travel'
urlpatterns = [
  url(r'^$', LoadMapView.as_view(), name='map'),  # dafaults to map
  url(r'^map$', LoadMapView.as_view(), name='map'),
  url(r'^graphs$', LoadGraphsView.as_view(), name='graphs'),
  url(r'^large-travels$', LoadLargeTravelsView.as_view(), name='large-travels'),
  url(r'^fromToMaps$', LoadFromToMapsView.as_view(), name='from-to'),
  url(r'^getMapData$', GetMapData.as_view()),
  url(r'^getGraphsData$', GetGraphsData.as_view()),
  url(r'^getLargeTravelsData$', GetLargeTravelsData.as_view()),
  url(r'^getFromToMapsData$', GetFromToMapsData.as_view())
]
