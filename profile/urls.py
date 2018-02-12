from django.conf.urls import url
from profile.views.LoadProfileByExpedition import LoadProfileByExpeditionView
from profile.views.LoadProfileByStop import LoadProfileByStopView
from profile.views.ODMatrix import ODMatrixView
from profile.views.Transfers import TransfersView, GetTransfersData
from profile.views.Trajectory import TrajectoryView

app_name = 'profile'
urlpatterns = [
    # html
    url(r'^expedition$', LoadProfileByExpeditionView.as_view(), name='expedition'),
    url(r'^stop$', LoadProfileByStopView.as_view(), name='stop'),
    url(r'^trajectory$', TrajectoryView.as_view(), name='trajectory'),
    url(r'^transfers$', TransfersView.as_view(), name='transfers'),
    url(r'^odmatrix$', ODMatrixView.as_view(), name='odmatrix'),
    # data
    url(r'^getTransfersData$', GetTransfersData.as_view(), name="getTransfersData"),
]
