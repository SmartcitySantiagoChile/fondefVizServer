from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from profile.esprofilehelper import ESProfileHelper

from localinfo.models import HalfHour


class LoadProfileByExpeditionView(View):
    def __init__(self):
        """ Constructor """
        super(LoadProfileByExpeditionView, self).__init__()

        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/byExpedition.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]

        context = {}
        context['data_filter'] = self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)


class GetAvailableDays(View):

    def get(self, request):

        self.es_helper = ESProfileHelper()
        available_days = self.es_helper.ask_for_available_days()

        response = {}
        response['availableDays'] = available_days

        return JsonResponse(response)


class GetAvailableRoutes(View):

    def get(self, request):

        self.es_helper = ESProfileHelper()
        available_days, op_dict = self.es_helper.ask_for_available_routes()

        response = {}
        response['availableRoutes'] = available_days
        response['operatorDict'] = op_dict

        return JsonResponse(response)


class GetLoadProfileByExpeditionData(View):
    def __init__(self):
        """ constructor """
        super(GetLoadProfileByExpeditionData, self).__init__()
        self.es_helper = ESProfileHelper()
        self.context = {}

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        startDate = request.GET.get('startDate')
        endDate = request.GET.get('endDate')
        route = request.GET.get('authRoute')
        licensePlate = request.GET.getlist('licensePlate[]')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        expeditionId = request.GET.getlist('expeditionId[]')
        halfHour = request.GET.getlist('halfHour[]')

        esQuery = self.es_helper.get_base_query()

        existsParameters = False
        if expeditionId:
            esQuery = esQuery.filter('terms', expeditionDayId=expeditionId)
            existsParameters = True
        if route:
            esQuery = esQuery.filter('term', route=route)
            existsParameters = True
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if licensePlate:
            esQuery = esQuery.filter('terms', licensePlate=licensePlate)
        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)
        if period:
            esQuery = esQuery.filter('terms', timePeriodInStartTime=period)
        if halfHour:
            halfHour = map(lambda x: int(x), halfHour)
            esQuery = esQuery.filter('terms', halfHourInStartTime=halfHour)

        if not existsParameters or startDate is None or endDate is None:
            raise ESQueryParametersDoesNotExist()

        esQuery = esQuery.filter("range", expeditionStartTime={
            "gte": startDate[:10] + "||/d",
            "lte": endDate[:10] + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })
        print(esQuery.to_dict())

        esQuery = esQuery.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'loadProfile',
                                  'expeditionDayId', 'userStopName', 'expandedAlighting', 'expandedBoarding',
                                  'expeditionStopOrder', 'stopDistanceFromPathStart', 'expeditionStartTime',
                                  'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                  'dayType', 'timePeriodInStopTime', 'fulfillment', "busStation"])

        return esQuery

    def cleanData(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value and value < 0) else value

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
        """ expedition data """
        response = {}
        response['trips'] = {}

        try:
            esQuery = self.buildQuery(request)
            response['trips'] = self.transformESAnswer(esQuery)
            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)
