from django.conf.urls import url
from .views.LoadIndicatorsByTravelTime import LoadIndicatorsByTravelTimeView, GetLoadIndicatorsByTravelTimeData


app_name = 'indicators'
urlpatterns = [
  url(r'^time$', LoadIndicatorsByTravelTimeView.as_view(), name='time'),
  url(r'^getTimeData$', GetLoadIndicatorsByTravelTimeData.as_view()),
]
