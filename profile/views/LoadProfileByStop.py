from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A, MultiSearch
from errors import ESQueryParametersDoesNotExist, ESQueryStopParameterDoesNotExist, ESQueryResultEmpty
from LoadProfileGeneric import LoadProfileGeneric

class LoadProfileByStopView(LoadProfileGeneric):
    ''' '''

    def __init__(self):
        ''' contructor '''

        esTSStopQuery = Search()
        esTSStopQuery = esTSStopQuery[:0]
        aggs = A('terms', field = "authStopCode", size=15000)
        esTSStopQuery.aggs.bucket('unique', aggs)

        esUserStopQuery = Search()
        esUserStopQuery = esUserStopQuery[:0]
        aggs = A('terms', field = "userStopCode", size=15000)
        esUserStopQuery.aggs.bucket('unique', aggs)
 
        esQueryDict = {}
        esQueryDict['authorityStopCodes'] = esTSStopQuery
        esQueryDict['userStopCodes'] = esUserStopQuery
 
        super(LoadProfileByStopView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/byStop.html"

        return render(request, template, self.context)


class GetLoadProfileByStopData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def buildQuery(self, request):
        ''' create es-query based on params given by user '''

        day = request.GET.get('day')
        fromDate = request.GET.get('from')
        toDate = request.GET.get('to')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        stopCode = request.GET.get('stopCode')

        # get list of profile*
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=LoadProfileGeneric.INDEX_NAME)
        
        existsParameters = False
        if stopCode:
            esQuery = esQuery.query(Q('term', authStopCode=stopCode)|Q('term', userStopCode=stopCode))
            existsParameters = True
        else:
            raise ESQueryStopParameterDoesNotExist()

        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)
            existsParameters = True
        if period:
            esQuery = esQuery.filter('terms', timePeriodInStopTime=period)
            existsParameters = True
        
        if not existsParameters:
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
                                  'dayType', 'timePeriodInStopTime', 'loadProfile'])
        return esQuery
 
    def cleanData(self, data):
        ''' round to zero values between [-1, 0]'''
        value = float(data)
        return 0 if (-1 < value and value < 0) else value

    def transformESAnswer(self, esQuery):
        ''' transform ES answer to something util to web client '''
        info = {}
        trips = {}

        for hit in esQuery.scan():
            data = hit.to_dict()

            if len(info.keys()) == 0:
                info['authorityStopCode'] = data['authStopCode']
                info['userStopCode'] = data['userStopCode']
                info['name'] = data['userStopName']

            expeditionId = data['expeditionDayId']

            trips[expeditionId] = {}
            trips[expeditionId]['capacity'] = int(data['busCapacity'])
            trips[expeditionId]['licensePlate'] = data['licensePlate']
            trips[expeditionId]['route'] = data['route']
            trips[expeditionId]['stopTime'] = "" if data['expeditionStopTime']=="0" else \
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
        ''' expedition data '''
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


