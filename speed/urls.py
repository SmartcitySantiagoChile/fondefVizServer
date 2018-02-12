from django.conf.urls import url

from speed.views.matrix import MatrixHTML
from speed.views.ranking import RankingHTML
from speed.views.variation import SpeedVariationHTML

app_name = 'speed'
urlpatterns = [
    # html
    url(r'^matrix$', MatrixHTML.as_view(), name='matrix'),
    url(r'^ranking$', RankingHTML.as_view(), name='ranking'),
    url(r'^variation$', SpeedVariationHTML.as_view(), name='variation')
]
