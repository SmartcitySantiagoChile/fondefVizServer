from django.conf.urls import url
from .views.LoadTravelsByTravelTime import LoadTravelsByTravelTimeView, GetLoadTravelsByTravelTimeData


app_name = 'travel'
urlpatterns = [
  url(r'^by_time$', LoadTravelsByTravelTimeView.as_view(), name='by_time'),
  url(r'^getDataByTime$', GetLoadTravelsByTravelTimeData.as_view()),
]
