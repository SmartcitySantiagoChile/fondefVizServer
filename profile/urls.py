from django.conf.urls import url
from .views.LoadProfileByExpedition import LoadProfileByExpeditionView, GetLoadProfileByExpeditionData
from .views.LoadProfileByStop import LoadProfileByStopView, GetLoadProfileByStopData, GetStopList
from .views.Trajectory import TrajectoryView

app_name='profile'
urlpatterns = [
  # html
  url(r'^expedition$', LoadProfileByExpeditionView.as_view(), name='expedition'),
  url(r'^stop$', LoadProfileByStopView.as_view(), name='stop'),
  url(r'^trajectory$', TrajectoryView.as_view(), name='trajectory'),
  # data
  url(r'^getExpeditionData$', GetLoadProfileByExpeditionData.as_view(), name="getExpeditionData"),
  url(r'^getStopData$', GetLoadProfileByStopData.as_view(), name="getStopData"),
  url(r'^getStopList$', GetStopList.as_view(), name="getStopList"),
]
