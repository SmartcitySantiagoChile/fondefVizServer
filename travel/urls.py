from django.conf.urls import url
from .views.LoadTravelsByTravelTime import LoadTravelsByTravelTimeView, GetLoadTravelsByTravelTimeData


app_name = 'travel'
urlpatterns = [
  url(r'^time$', LoadTravelsByTravelTimeView.as_view(), name='time'),
  url(r'^getTimeData$', GetLoadTravelsByTravelTimeData.as_view()),
]
