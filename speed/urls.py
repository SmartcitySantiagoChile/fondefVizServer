from django.conf.urls import url

from speed.views.matrix import MatrixHTML, GetAvailableDays, GetAvailableRoutes, GetMatrixData
from speed.views.ranking import RankingHTML, GetRankingData, GetSpeedByRoute
from speed.views.variation import SpeedVariationHTML, GetSpeedVariationData

app_name = 'speed'
urlpatterns = [
    # html
    url(r'^matrix$', MatrixHTML.as_view(), name='matrix'),
    url(r'^ranking$', RankingHTML.as_view(), name='ranking'),
    url(r'^variation$', SpeedVariationHTML.as_view(), name='variation'),
    # get data
    url(r'^getMatrixData$', GetMatrixData.as_view(), name='getMatrixData'),
    url(r'^getRankingData$', GetRankingData.as_view(), name='getRankingData'),
    url(r'^getSpeedByRoute$', GetSpeedByRoute.as_view(), name='getSpeedByRoute'),
    url(r'^getVariationData$', GetSpeedVariationData.as_view(), name='getSpeedVariationData'),
    # get available days
    url(r'^getAvailableDays$', GetAvailableDays.as_view(), name='getAvailableDays'),
    url(r'^getAvailableRoutes$', GetAvailableRoutes.as_view(), name='getAvailableRoutes'),
]
