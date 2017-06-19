from django.conf.urls import url
from . import views
from velocity.views import LoadMatrixView, getLoadMatrixData

urlpatterns = [
	url(r'^matrix$', LoadMatrixView.as_view(), name='matrix'),
	url(r'^getMatrixData$', getLoadMatrixData.as_view()),
	# url(r'^ranking$', LoadRankingView.as_view(), name='ranking'),
]
