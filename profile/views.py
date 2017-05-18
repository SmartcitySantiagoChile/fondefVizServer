from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A
# Create your views here.

from localinfo.models import TimePeriod

from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty

# elastic search index name 
INDEX_NAME="profiles"

class LoadProfileByExpeditionView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}
        self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        self.context['periods'] = TimePeriod.objects.filter(dayType='Laboral').order_by('id').values_list('transantiagoPeriod', flat=True)
        self.context['routes'] = self.getRouteList()

    def getRouteList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=INDEX_NAME)
        esQuery = esQuery[:0]
        #esQuery = esQuery.source(['ServicioSentido'])
        aggs = A('terms', field = 'ServicioSentido', size=1000)
        esQuery.aggs.bucket('unique_routes', aggs)
  
        routes = []
        for tag in esQuery.execute().aggregations.unique_routes.buckets:
            routes.append(tag.key)
        routes.sort()

        return routes

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
            esQuery = esQuery.filter('terms', Periodo=period)
            existsParameters = True
        
        if not existsParameters:
            raise ESQueryDoesNotHaveParameters()

        esQuery = esQuery.query('match', Cumplimiento='C')\
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada', 'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero'])

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
            trips[expeditionId]['info']['timeTripEnd'] = data['Hfin']
            stop = {}
            stop['name'] = data['NombreParada']
            stop['authStopCode'] = data['Paradero']
            stop['userStopCode'] = data['Paradero']
            stop['distOnRoute'] = data['DistEnRuta']
            stop['time'] = data['Tiempo']
            stop['order'] = int(data['Correlativo'])

            # to avoid movement of distribution chart
            loadProfile = float(data['Carga'])
            loadProfile = 0 if (-0.5 < loadProfile and loadProfile < 0) else loadProfile

            expandedGetIn = float(data['SubidasExpandidas'])
            expandedGetIn = 0 if (-0.5 < expandedGetIn and expandedGetIn < 0) else expandedGetIn

            expandedGetOut = float(data['BajadasExpandidas'])
            expandedGetOut = 0 if (-0.5 < expandedGetOut and expandedGetOut < 0) else expandedGetOut

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


