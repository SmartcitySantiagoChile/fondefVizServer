from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from datetime import datetime

from elasticsearch_dsl import Q
from errors import ESQueryParametersDoesNotExist, ESQueryStopParameterDoesNotExist, ESQueryResultEmpty

from localinfo.models import HalfHour
from profile.esprofilehelper import ESProfileHelper


class LoadProfileByStopView(View):
    def __init__(self):
        super(LoadProfileByStopView, self).__init__()
        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/byStop.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]
        context = {}
        context['data_filter'] = self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)


class GetLoadProfileByStopData(View):
    def __init__(self):
        """ constructor """
        super(GetLoadProfileByStopData, self).__init__()
        self.es_helper = ESProfileHelper()
        self.context = {}

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        startDate = request.GET.get('startDate')
        endDate = request.GET.get('endDate')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        stopCode = request.GET.get('stopCode')
        halfHour = request.GET.getlist('halfHour[]')

        esQuery = self.es_helper.get_base_query()

        existsParameters = False
        if stopCode:
            esQuery = esQuery.query(
                Q({'term': {"authStopCode.keyword": stopCode}}) | Q({'term': {"userStopCode.keyword": stopCode}}) | Q(
                    {'term': {"userStopName.keyword": stopCode}}))
            existsParameters = True
        else:
            raise ESQueryStopParameterDoesNotExist()

        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)
        if period:
            esQuery = esQuery.filter('terms', timePeriodInStopTime=period)
        if halfHour:
            esQuery = esQuery.filter('terms', halfHour=halfHour)

        if not existsParameters or startDate is None or endDate is None:
            raise ESQueryParametersDoesNotExist()

        esQuery = esQuery.filter("range", expeditionStartTime={
            "gte": startDate[:10] + "||/d",
            "lte": endDate[:10] + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        esQuery = esQuery.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'expeditionDayId',
                                  'userStopName', 'expandedAlighting', 'expandedBoarding', 'fulfillment',
                                  'stopDistanceFromPathStart', 'expeditionStartTime',
                                  'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                  'dayType', 'timePeriodInStopTime', 'loadProfile', 'busStation'])
        return esQuery

    def cleanData(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value and value < 0) else value

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        info = {}
        trips = {}

        for hit in esQuery.scan():
            data = hit.to_dict()

            if len(info.keys()) == 0:
                info['authorityStopCode'] = data['authStopCode']
                info['userStopCode'] = data['userStopCode']
                info['name'] = data['userStopName']
                info['busStation'] = data['busStation'] == "1"

            expeditionId = data['expeditionDayId']

            trips[expeditionId] = {}
            trips[expeditionId]['capacity'] = int(data['busCapacity'])
            trips[expeditionId]['licensePlate'] = data['licensePlate']
            trips[expeditionId]['route'] = data['route']
            trips[expeditionId]['stopTime'] = "" if data['expeditionStopTime'] == "0" else \
                data['expeditionStopTime'].replace('T', ' ').replace('.000Z', '')
            trips[expeditionId]['stopTimePeriod'] = data['timePeriodInStopTime']
            trips[expeditionId]['dayType'] = data['dayType']
            trips[expeditionId]['distOnPath'] = data['stopDistanceFromPathStart']

            # to avoid movement of distribution chart
            trips[expeditionId]['loadProfile'] = self.cleanData(data['loadProfile'])
            trips[expeditionId]['expandedGetIn'] = self.cleanData(data['expandedBoarding'])
            trips[expeditionId]['expandedLanding'] = self.cleanData(data['expandedAlighting'])

        if len(info.keys()) == 0:
            raise ESQueryResultEmpty()

        result = {}
        result['info'] = info
        result['trips'] = trips

        return result

    def get(self, request):
        """ expedition data """
        response = {}

        try:
            esQuery = self.buildQuery(request)
            response = self.transformESAnswer(esQuery)
            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryStopParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)


class GetStopList(View):
    """ list when user ask for stop """

    def __init__(self):
        """ constructor """
        super(GetStopList, self).__init__()
        self.es_helper = ESProfileHelper()
        self.context = {}

    def get(self, request):
        """ expedition data """

        term = request.GET.get("term")

        results = self.es_helper.ask_for_stop(term)

        response = {}
        response["items"] = []

        for _, result in results.iteritems():
            resultList = []
            for tag in result:
                resultList.append({"id": tag, "text": tag})

            response["items"] += resultList

        return JsonResponse(response, safe=False)
