from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from esapi.views.bip import AvailableDays as BAD, BipTransactionByOperatorData
from esapi.views.odbyroute import AvailableDays as ODAD, AvailableRoutes as ODAR, ODMatrixData
from esapi.views.opdata import OPDataByAuthRouteCode as ODBAR
from esapi.views.paymentfactor import AvailableDays as PFAD, PaymentFactorData
from esapi.views.profile import LoadProfileByStopData, AvailableDays, AvailableRoutes, \
    LoadProfileByExpeditionData, LoadProfileByTrajectoryData, BoardingAndAlightingAverageByStops
from esapi.views.resume import GlobalData, AvailableDays as StatisticAD
from esapi.views.shape import GetBaseInfo, GetRouteInfo, GetUserRoutesByOP
from esapi.views.speed import AvailableDays as SAD, AvailableRoutes as SAR, MatrixData, RankingData, SpeedByRoute, \
    SpeedVariation
from esapi.views.stop import MatchedStopData
from esapi.views.trip import ResumeData, AvailableDays as TAD, MapData, LargeTravelData, FromToMapData, StrategiesData, \
    TransfersData, MultiRouteData

app_name = 'esapi'
urlpatterns = [
    # profile index
    url(r'^profile/loadProfileByStopData/$', login_required(LoadProfileByStopData.as_view()),
        name='loadProfileByStopData'),
    url(r'^profile/loadProfileByExpeditionData/$', login_required(LoadProfileByExpeditionData.as_view()),
        name='loadProfileByExpeditionData'),
    url(r'^profile/loadProfileByTrajectoryData/$', login_required(LoadProfileByTrajectoryData.as_view()),
        name='loadProfileByTrajectoryData'),
    url(r'^profile/boardingAndAlightingAverageByStops/$', login_required(BoardingAndAlightingAverageByStops.as_view()),
        name='boardingAndAlightingAverageByStops'),
    url(r'^profile/availableDays/$', login_required(AvailableDays.as_view()), name='availableProfileDays'),
    url(r'^profile/availableRoutes/$', login_required(AvailableRoutes.as_view()), name='availableProfileRoutes'),

    # odbyroute index
    url(r'^odbyroute/matrixData/$', login_required(ODMatrixData.as_view()), name='ODMatrixData'),
    url(r'^odbyroute/availableDays/$', login_required(ODAD.as_view()), name='availableODDays'),
    url(r'^odbyroute/availableRoutes/$', login_required(ODAR.as_view()), name='availableODRoutes'),

    # general index
    url(r'^resume/data/$', login_required(GlobalData.as_view()), name='resumeData'),
    url(r'^resume/availableDays/$', login_required(StatisticAD.as_view()), name='availableStatisticDays'),

    # speed index
    url(r'^speed/availableDays/$', login_required(SAD.as_view()), name='availableSpeedDays'),
    url(r'^speed/availableRoutes/$', login_required(SAR.as_view()), name='availableSpeedRoutes'),
    url(r'^speed/matrixData/$', login_required(MatrixData.as_view()), name='matrixData'),
    url(r'^speed/rankingData/$', login_required(RankingData.as_view()), name='rankingData'),
    url(r'^speed/speedByRoute/$', login_required(SpeedByRoute.as_view()), name='speedByRoute'),
    url(r'^speed/speedVariation/$', login_required(SpeedVariation.as_view()), name='speedVariation'),

    # trip index
    url(r'^trip/resumeData/$', login_required(ResumeData.as_view()), name='resumeTripData'),
    url(r'^trip/largeTravelData/$', login_required(LargeTravelData.as_view()), name='largeTravelData'),
    url(r'^trip/fromToMapData/$', login_required(FromToMapData.as_view()), name='fromToMapData'),
    url(r'^trip/strategiesData/$', login_required(StrategiesData.as_view()), name='tripStrategiesData'),
    url(r'^trip/mapData/$', login_required(MapData.as_view()), name='tripMapData'),
    url(r'^trip/availableDays/$', login_required(TAD.as_view()), name='availableTripDays'),
    url(r'^trip/transfersData/$', login_required(TransfersData.as_view()), name='transfersData'),
    url(r'^trip/multiRouteData/$', login_required(MultiRouteData.as_view()), name='multiRouteData'),

    # stop indes
    url(r'^stop/matchedStopData/$', login_required(MatchedStopData.as_view()), name='matchedStopData'),

    # shape index
    # url(r'^shape', login_required(DeleteData.as_view()), name='deleteData'),
    url(r'^shape/base/$', login_required(GetBaseInfo.as_view()), name='shapeBase'),
    url(r'^shape/route/$', login_required(GetRouteInfo.as_view()), name='shapeRoute'),
    url(r'^shape/userRoutes/$', login_required(GetUserRoutesByOP.as_view()), name='shapeUserRoutes'),

    # paymentfactor index
    url(r'^paymentfactor/availableDays/$', login_required(PFAD.as_view()), name='availablePaymentfactorDays'),
    url(r'^paymentfactor/data/$', login_required(PaymentFactorData.as_view()), name='paymentfactorData'),

    # bip index
    url(r'^bip/availableDays/$', login_required(BAD.as_view()), name='availableBipDays'),
    url(r'^bip/bipTransactionByOperatorData/$', login_required(BipTransactionByOperatorData.as_view()),
        name='operatorBipData'),

    # opdata index
    url(r'^opdata/opDataByAuthRouteCode/', login_required(ODBAR.as_view()), name='opdataAuthRoute'),
]
