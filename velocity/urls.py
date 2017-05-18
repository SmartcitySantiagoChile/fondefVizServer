from django.conf.urls import url
from . import views
from velocity.views import LoadRankingView

urlpatterns = [
	url(r'^ranking$', LoadRankingView.as_view(), name='ranking'),
	# url(r'^getRankingData$', GetLoadRankingData.as_view()),
]
