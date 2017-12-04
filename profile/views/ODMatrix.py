from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from elasticsearch_dsl import Q
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from profile.esprofilehelper import ESProfileHelper

from localinfo.models import HalfHour
from datetime import datetime


class ODMatrixView(View):
    def __init__(self):
        """ Constructor """
        super(ODMatrixView, self).__init__()

        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()
        self.base_params["routes"] = self.es_helper.get_unique_list_query("route", size=10000)

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
        self.es_helper = ESProfileHelper()
        self.context = {}

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        day = request.GET.get('day')
        route = request.GET.getlist('route[]')
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
            esQuery = esQuery.filter('terms', route=route)
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
            # when this field exists
            # esQuery = esQuery.filter('terms', halfHour=halfHour)
            halfHourObjs = HalfHour.objects.filter(longName__in=halfHour).order_by("id")

            dateRef = datetime(1970, 1, 1)
            timeRanges = None
            for day in [day]:
                for index, halfHourObj in enumerate(halfHourObjs):
                    startHour = halfHourObj.longName.split('-')[0]
                    endHour = halfHourObj.longName.split('-')[1]
                    startDate = day + " " + startHour
                    endDate = day + " " + endHour

                    startRange = int((datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S") - dateRef).total_seconds())
                    endRange = int((datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S") - dateRef).total_seconds())

                    timeRange = Q("range", expeditionStartTime={
                        "gte": startRange,
                        "lte": endRange,
                        "format": "epoch_second"
                    })
                    if timeRanges is None:
                        timeRanges = timeRange
                    else:
                        timeRanges = timeRanges | timeRange

            esQuery = esQuery.query(timeRanges)

        if not existsParameters or day is None:
            raise ESQueryParametersDoesNotExist()

        esQuery = esQuery.filter("range", expeditionStartTime={
            "gte": day + "||/d",
            "lte": day + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

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
            # esQuery = self.buildQuery(request)
            # response['trips'] = self.transformESAnswer(esQuery)
            response["data"] = {
                "matrix": []
            }
            stops = ["PI528", "PI529", "PI167", "PI486", "PI487", "PI488", "PI489", "PI94", "PI530", "PI531", "PI532",
                     "PI533", "PI378", "PI379", "PI380", "PI565", "PI1345", "PI1344", "PI1346", "PI230", "PI231",
                     "PI232", "PI233", "PI234", "PI235", "PI236", "PI387", "PI388", "PI389", "PI534", "PI535", "PI536",
                     "PI537", "PI538", "PI539", "PI1461", "PI38", "PI39", "PI40", "PI41", "PI42", "PI43", "PI44",
                     "PI540", "PI541", "PI542", "PI543", "PI544", "PI545", "PI546", "PA289", "PA290", "PA433", "PA434",
                     "PA435", "PA436", "PA658", "PA438", "PA439", "PA440", "PA666", "PA442", "PD524", "PD525", "PD644",
                     "PD589", "PD115", "PD116", "PD590", "PD592", "PD645", "PD535", "PD571", "PD572", "PD573", "PD1322",
                     "PD537", "PD538", "PD1323", "PD539", "PD540", "PD541", "PD542", "PD543"]

            from random import randint
            for stop in stops:
                destination = []
                for stop2 in stops[::-1]:
                    value = randint(0,1000)
                    if stop == stop2:
                        value = 0
                    value = '-' if value == 0 else value
                    destination.append({"name": stop2, "value": value})
                row = {
                    "origin": stop,
                    "destination": destination
                }
                response["data"]["matrix"].append(row)

            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)
