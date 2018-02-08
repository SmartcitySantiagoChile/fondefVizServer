from django.conf.urls import url
from profile.views.LoadProfileByExpedition import LoadProfileByExpeditionView, GetLoadProfileByExpeditionData, \
    GetAvailableDays, GetAvailableRoutes
from profile.views.LoadProfileByStop import LoadProfileByStopView, GetLoadProfileByStopData, GetStopList
from profile.views.ODMatrix import ODMatrixView, GetODMatrixData
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
    url(r'^getExpeditionData$', GetLoadProfileByExpeditionData.as_view(), name="getExpeditionData"),
    url(r'^getStopData$', GetLoadProfileByStopData.as_view(), name="getStopData"),
    url(r'^getStopList$', GetStopList.as_view(), name="getStopList"),
    url(r'^getTransfersData$', GetTransfersData.as_view(), name="getTransfersData"),
    url(r'^getODMatrixData$', GetODMatrixData.as_view(), name="getODMatrixData"),
    # available data
    url(r'^getAvailableDays$', GetAvailableDays.as_view(), name="getAvailableDays"),
    url(r'^getAvailableRoutes$', GetAvailableRoutes.as_view(), name="getAvailableRoutes"),
]
