from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A, MultiSearch
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty

# elastic search index name 
INDEX_NAME="profiles"

class LoadProfileByExpeditionView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}

        routes, dayTypes, timePeriods = self.getParamsList()
        self.context['dayTypes'] = dayTypes
        self.context['periods'] = timePeriods
        self.context['routes'] = routes

    def getParamsList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT

        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "ServicioSentido", size=1000)
        esRouteQuery.aggs.bucket('unique_routes', aggs)

        esDayTypeQuery = Search()
        esDayTypeQuery = esDayTypeQuery[:0]
        aggs = A('terms', field = "TipoDia", size=10)
        esDayTypeQuery.aggs.bucket('unique_day_types', aggs)

        esTimePeriodQuery = Search()
        esTimePeriodQuery = esDayTypeQuery[:0]
        aggs = A('terms', field = "PeriodoTSExpedicion", size=50)
        esTimePeriodQuery.aggs.bucket('unique_time_periods', aggs)
  
        multiSearch = MultiSearch(using=client, index=INDEX_NAME)
        multiSearch = multiSearch.add(esRouteQuery).add(esDayTypeQuery).add(esTimePeriodQuery)

        # to see the query generated
        #print multiSearch.to_dict()
        responses = multiSearch.execute()

        routes = []
        for tag in responses[0].aggregations.unique_routes.buckets:
            routes.append(tag.key)
        routes.sort()

        dayTypes = []
        for tag in responses[1].aggregations.unique_day_types.buckets:
            dayTypes.append(tag.key)
        dayTypes.sort()

        timePeriods = []
        for tag in responses[2].aggregations.unique_time_periods.buckets:
            timePeriods.append(tag.key)
        timePeriods.sort()

        return routes, dayTypes, timePeriods

    def getESRouteQuery(self, ESClient):
        ''' create elastic search query to get route list '''


    def get(self, request):
        template = "profile/expedition.html"

        return render(request, template, self.context)


class GetLoadProfileByExpeditionData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def buildQuery(self, request):
        ''' create es-query based on params given by user '''

        fromDate = request.GET.get('from', None)
        toDate = request.GET.get('to', None)
        route = request.GET.get('route', None)
        licensePlate = request.GET.getlist('licensePlate[]', None)
        dayType = request.GET.getlist('dayType[]', None)
        period = request.GET.getlist('period[]', None)
        expeditionId = request.GET.getlist('expeditionId[]', None)

        # get list of profile*
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index="profiles")
        
        existsParameters = False
        if expeditionId:
            esQuery = esQuery.filter('terms', idExpedicion=expeditionId)
            existsParameters = True
        if route:
            esQuery = esQuery.filter('term', ServicioSentido=route)
            existsParameters = True
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if licensePlate:
            esQuery = esQuery.filter('terms', Patente=licensePlate)
            existsParameters = True
        if dayType:
            esQuery = esQuery.filter('terms', TipoDia=dayType)
            existsParameters = True
        if period:
            esQuery = esQuery.filter('terms', PeriodoTSExpedicion=period)
            existsParameters = True
        
        if not existsParameters:
            raise ESQueryDoesNotHaveParameters()

        esQuery = esQuery.filter('term', Cumplimiento='C')\
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada', 'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero', 'ParaderoUsuario', 'PeriodoTSExpedicion', 'TipoDia', 'PeriodoTSParada'])

        if esQuery.execute().hits.total == 0:
            raise ESQueryResultEmpty()

        return esQuery
 
    def transformESAnswer(self, esQuery):
        ''' transform ES answer to something util to web client '''
        trips = {}

        for hit in esQuery.scan():
            data = hit.to_dict()

            expeditionId = data['idExpedicion']
            if expeditionId not in trips:
                trips[expeditionId] = {'info': {}, 'stops': []}

            trips[expeditionId]['info']['capacity'] = int(data['Capacidad'])
            trips[expeditionId]['info']['licensePlate'] = data['Patente']
            trips[expeditionId]['info']['route'] = data['ServicioSentido']
            trips[expeditionId]['info']['timeTripInit'] = data['Hini']
            trips[expeditionId]['info']['authTimePeriod'] = data['PeriodoTSExpedicion']
            trips[expeditionId]['info']['timeTripEnd'] = data['Hfin']
            trips[expeditionId]['info']['dayType'] = data['TipoDia']
            stop = {}
            stop['name'] = data['NombreParada']
            stop['authStopCode'] = data['Paradero']
            stop['userStopCode'] = data['ParaderoUsuario']
            stop['authTimePeriod'] = data['PeriodoTSParada']
            stop['distOnRoute'] = data['DistEnRuta']
            stop['time'] = data['Tiempo']
            stop['order'] = int(data['Correlativo'])

            # to avoid movement of distribution chart
            loadProfile = float(data['Carga'])
            loadProfile = 0 if (-1 < loadProfile and loadProfile < 0) else loadProfile

            expandedGetIn = float(data['SubidasExpandidas'])
            expandedGetIn = 0 if (-1 < expandedGetIn and expandedGetIn < 0) else expandedGetIn

            expandedGetOut = float(data['BajadasExpandidas'])
            expandedGetOut = 0 if (-1 < expandedGetOut and expandedGetOut < 0) else expandedGetOut

            stop['loadProfile'] = loadProfile
            stop['expandedGetIn'] = expandedGetIn
            stop['expandedGetOut'] = expandedGetOut
            trips[expeditionId]['stops'].append(stop)

        for expeditionId in trips:
            trips[expeditionId]['stops'] = sorted(trips[expeditionId]['stops'], 
                 key=lambda record: record['order'])

        return trips

    def get(self, request):
        ''' expedition data '''
        response = {}
        response['trips'] = {}

        try:
            esQuery = self.buildQuery(request)
            response['trips'] = self.transformESAnswer(esQuery)
            # debug
            #response['query'] = esQuery.to_dict()
            #return JsonResponse(response, safe=False)
            #response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)


