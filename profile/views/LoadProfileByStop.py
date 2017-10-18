from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from datetime import datetime

from elasticsearch_dsl import Search, Q, A, MultiSearch
from elasticsearch_dsl.query import Match
from errors import ESQueryParametersDoesNotExist, ESQueryStopParameterDoesNotExist, ESQueryResultEmpty
from LoadProfileGeneric import LoadProfileGeneric

from localinfo.models import HalfHour


class LoadProfileByStopView(LoadProfileGeneric):
    """ """

    def __init__(self):
        esQueryDict = {}
        super(LoadProfileByStopView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/byStop.html"

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)
        self.context['minutes'] = minutes

        return render(request, template, self.context)


class GetLoadProfileByStopData(View):
    """ """

    def __init__(self):
        """ constructor """
        super(GetLoadProfileByStopData, self).__init__()
        self.context={}

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        day = request.GET.get('day')
        #fromDate = request.GET.get('from')
        #toDate = request.GET.get('to')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        stopCode = request.GET.get('stopCode')
        halfHour = request.GET.getlist('halfHour[]')

        # get list of profile*
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=LoadProfileGeneric.INDEX_NAME)
        
        existsParameters = False
        if stopCode:
            esQuery = esQuery.query(Q({'term': {"authStopCode.keyword": stopCode}})|Q({'term': {"userStopCode.keyword":stopCode}})|Q({'term': {"userStopName.keyword": stopCode}}))
            existsParameters = True
        else:
            raise ESQueryStopParameterDoesNotExist()

        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)
        if period:
            esQuery = esQuery.filter('terms', timePeriodInStopTime=period)
        if halfHour:
            # when this field exists
            #esQuery = esQuery.filter('terms', halfHour=halfHour)
            halfHourObjs = HalfHour.objects.filter(longName__in=halfHour).order_by("id")

            dateRef = datetime(1970, 1, 1)
            timeRanges = None
            for day in [day]:
                for index, halfHourObj in enumerate(halfHourObjs):
                    startHour = halfHourObj.longName.split('-')[0]
                    endHour = halfHourObj.longName.split('-')[1]
                    startDate = day + " " + startHour
                    endDate = day + " " + endHour

                    startRange = int((datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")-dateRef).total_seconds())
                    endRange = int((datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S")-dateRef).total_seconds())

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
                data['expeditionStopTime'].replace('T',' ').replace('.000Z', '')
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
            #response['query'] = esQuery.to_dict()
            #return JsonResponse(response, safe=False)
            #response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryStopParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)



class GetStopList(View):
    """ list when user ask for stop """

    def __init__(self):
        """ constructor """
        super(GetStopList, self).__init__()
        self.context={}

    def get(self, request):
        """ expedition data """

        term = request.GET.get("term")

        multiSearch = MultiSearch(using=settings.ES_CLIENT, index=LoadProfileGeneric.INDEX_NAME)

        esAuthStopQuery = Search().query(Match(authStopCode={"query": term, "analyzer": "standard"}))[:0]
        aggregation = A('terms', field="authStopCode.keyword", size=15000)
        esAuthStopQuery.aggs.bucket('unique', aggregation)

        esUserStopQuery = Search().query(Match(userStopCode={"query": term, "analyzer": "standard"}))[:0]
        aggregation = A('terms', field="userStopCode.keyword", size=15000)
        esUserStopQuery.aggs.bucket('unique', aggregation)

        esUserStopNameQuery = Search().query(Match(userStopName={"query": term, "operator": "and"}))[:0]
        aggregation = A('terms', field="userStopName.keyword", size=15000)
        esUserStopNameQuery.aggs.bucket('unique', aggregation)

        multiSearch = multiSearch.add(esAuthStopQuery)
        multiSearch = multiSearch.add(esUserStopQuery)
        multiSearch = multiSearch.add(esUserStopNameQuery)

        results = multiSearch.execute()

        response = {}
        response["items"] = []

        for result in results:
            resultList = []
            for tag in result.aggregations.unique.buckets:
                if tag.doc_count == 0:
                    continue
                if "key_as_string" in tag:
                    resultList.append({"id": tag.key_as_string, "text": tag.key_as_string})
                else:
                    resultList.append({"id": tag.key, "text": tag.key})

            response["items"] += resultList

        # debug
        #response['query'] = esQuery.to_dict()
        #return JsonResponse(response, safe=False)
        #response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}

        return JsonResponse(response, safe=False)
