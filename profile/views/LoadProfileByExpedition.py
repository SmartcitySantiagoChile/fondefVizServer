from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A, MultiSearch
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from LoadProfileGeneric import LoadProfileGeneric

class LoadProfileByExpeditionView(LoadProfileGeneric):
    ''' '''

    def __init__(self):
        ''' contructor '''

        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "ServicioSentido", size=1000)
        esRouteQuery.aggs.bucket('unique', aggs)
 
        esQueryDict = {}
        esQueryDict['routes'] = esRouteQuery
        
        super(LoadProfileByExpeditionView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/byExpedition.html"

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
        esQuery = Search(using=client, index=LoadProfileGeneric.INDEX_NAME)
        
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

        return esQuery
 
    def cleanData(self, data):
        ''' round to zero values between [-1, 0]'''
        value = float(data)
        return 0 if (-1 < value and value < 0) else value

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
            stop['distOnPath'] = data['DistEnRuta']
            stop['stopTime'] = data['Tiempo']
            stop['order'] = int(data['Correlativo'])

            # to avoid movement of distribution chart
            stop['loadProfile'] =  self.cleanData(data['Carga'])
            stop['expandedGetIn'] = self.cleanData(data['SubidasExpandidas'])
            stop['expandedGetOut'] = self.cleanData(data['BajadasExpandidas'])
            trips[expeditionId]['stops'].append(stop)

        for expeditionId in trips:
            trips[expeditionId]['stops'] = sorted(trips[expeditionId]['stops'], 
                 key=lambda record: record['order'])

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

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


