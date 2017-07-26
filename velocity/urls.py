from django.conf.urls import url
from . import views
from velocity.views import LoadMatrixView, getLoadMatrixData, LoadRankingView, getLoadRankingData, getLoadSpeedByRoute, getLoadSpeedVariationView, getLoadSpeedVariationData

urlpatterns = [
	url(r'^matrix$', LoadMatrixView.as_view(), name='matrix'),
	url(r'^getMatrixData$', getLoadMatrixData.as_view()),
	url(r'^ranking$', LoadRankingView.as_view(), name='ranking'),
	url(r'^getRankingData$', getLoadRankingData.as_view()),
	url(r'^getSpeedByRoute$', getLoadSpeedByRoute.as_view()),
	url(r'^variation$', getLoadSpeedVariationView.as_view(), name='variation'),
	url(r'^getVariationData$', getLoadSpeedVariationData.as_view()),
]
