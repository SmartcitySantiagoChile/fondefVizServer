from django.conf.urls import url
from speed.views2 import LoadMatrixView, getLoadMatrixData, LoadRankingView, getLoadRankingData, getLoadSpeedByRoute, \
    getLoadSpeedVariationView, getLoadSpeedVariationData
from speed.views.matrix import MatrixHTML, GetAvailableDays, GetAvailableRoutes, getMatrixData

app_name = 'speed'
urlpatterns = [
    # html
    url(r'^matrix$', MatrixHTML.as_view(), name='matrix'),
    url(r'^ranking$', LoadRankingView.as_view(), name='ranking'),
    url(r'^variation$', getLoadSpeedVariationView.as_view(), name='variation'),
    # get data
    url(r'^getMatrixData$', getMatrixData.as_view(), name='getMatrixData'),
    url(r'^getRankingData$', getLoadRankingData.as_view(), name='getRankingData'),
    url(r'^getSpeedByRoute$', getLoadSpeedByRoute.as_view(), name='getSpeedByRoute'),
    url(r'^getVariationData$', getLoadSpeedVariationData.as_view(), name='getVariationData'),
    # get available days
    url(r'^getAvailableDays$', GetAvailableDays.as_view(), name='getAvailableDays'),
    url(r'^getAvailableRoutes$', GetAvailableRoutes.as_view(), name='getAvailableRoutes'),
]
