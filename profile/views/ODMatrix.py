from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from elasticsearch_dsl import Q
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from profile.esprofilehelper import ESODByRouteHelper

from localinfo.models import HalfHour
from datetime import datetime


class ODMatrixView(View):
    def __init__(self):
        """ Constructor """
        super(ODMatrixView, self).__init__()

        self.es_helper = ESODByRouteHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/odmatrix.html"

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)

        context = self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        context['minutes'] = minutes

        return render(request, template, context)


class GetODMatrixData(View):

    def __init__(self):
        """ constructor """
        super(GetODMatrixData, self).__init__()
        self.es_helper = ESODByRouteHelper()
        self.context = {}

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        trips = {}

        for hit in esQuery.scan():
            data = hit.to_dict()

            expeditionId = data['expeditionDayId']
            if expeditionId not in trips:
                trips[expeditionId] = {'info': {}, 'stops': []}

            trips[expeditionId]['info']['capacity'] = int(data['busCapacity'])
            trips[expeditionId]['info']['licensePlate'] = data['licensePlate']
            trips[expeditionId]['info']['route'] = data['route']
            trips[expeditionId]['info']['authTimePeriod'] = data['timePeriodInStartTime']
            trips[expeditionId]['info']['timeTripInit'] = data['expeditionStartTime'].replace('T', ' ').replace('.000Z',
                                                                                                                '')
            trips[expeditionId]['info']['timeTripEnd'] = data['expeditionEndTime'].replace('T', ' ').replace('.000Z',
                                                                                                             '')
            trips[expeditionId]['info']['dayType'] = data['dayType']

            stop = {}
            stop['name'] = data['userStopName']
            stop['authStopCode'] = data['authStopCode']
            stop['userStopCode'] = data['userStopCode']
            stop['busStation'] = data['busStation'] == "1"
            stop['authTimePeriod'] = data['timePeriodInStopTime']
            stop['distOnPath'] = data['stopDistanceFromPathStart']
            stop['stopTime'] = "" if data['expeditionStopTime'] == "0" else \
                data['expeditionStopTime'].replace('T', ' ').replace('.000Z', '')
            stop['order'] = int(data['expeditionStopOrder'])

            # to avoid movement of distribution chart
            stop['loadProfile'] = self.cleanData(data['loadProfile'])
            stop['expandedGetIn'] = self.cleanData(data['expandedBoarding'])
            stop['expandedGetOut'] = self.cleanData(data['expandedAlighting'])
            trips[expeditionId]['stops'].append(stop)

        for expeditionId in trips:
            trips[expeditionId]['stops'] = sorted(trips[expeditionId]['stops'],
                                                  key=lambda record: record['order'])

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips

    def get(self, request):
        """ data data """

        day = request.GET.get('day')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        route = request.GET.get('route')

        response = {}
        response['data'] = {}
        try:
            if not route:
                raise ESQueryRouteParameterDoesNotExist()

            matrix, max_value = self.es_helper.ask_for_od(route, period, dayType, day)

            # esQuery = self.buildQuery(request)
            # response['trips'] = self.transformESAnswer(esQuery)
            response["data"] = {
                "matrix": matrix,
                "maximum": max_value
            }

            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)
