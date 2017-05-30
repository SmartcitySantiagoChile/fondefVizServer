from django.conf.urls import url
from .views.LoadProfileByExpedition import LoadProfileByExpeditionView, GetLoadProfileByExpeditionData
from .views.LoadProfileByStop import LoadProfileByStopView, GetLoadProfileByStopData

app_name='profile'
urlpatterns = [
  url(r'^expedition$', LoadProfileByExpeditionView.as_view(), name='expedition'),
  url(r'^getExpeditionData$', GetLoadProfileByExpeditionData.as_view()),
  url(r'^stop$', LoadProfileByStopView.as_view(), name='stop'),
  url(r'^getStopData$', GetLoadProfileByStopData.as_view()),
]
