from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
# Create your views here.

from localinfo.models import TimePeriod

from errors import ESQueryDoesNotHaveParameters

class LoadProfileByExpeditionView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}
        self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        self.context['periods'] = TimePeriod.objects.filter(dayType='Laboral').order_by('id').values_list('transantiagoPeriod', flat=True)

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
        client = Elasticsearch("172.17.57.47:9200", http_auth=('elastic', 'changeme'))
        esQuery = Search(using=client, index="profiles")
        
        existsParameters = False
        if expeditionId:
            esQuery = esQuery.query('terms', idExpedicion=expeditionId)
            existsParameters = True
        if route:
            esQuery = esQuery.query('term', ServicioSentido=route)
            existsParameters = True
        if licensePlate:
            esQuery = esQuery.query('terms', Patente=licensePlate)
            existsParameters = True
        if dayType:
            esQuery = esQuery.query('terms', TipoDia=dayType)
            existsParameters = True
        if period:
            esQuery = esQuery.query('terms', Periodo=period)
            existsParameters = True
        
        if not existsParameters:
            raise ESQueryDoesNotHaveParameters()

        esQuery = esQuery.query('match', Cumplimiento='C')\
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada', 'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero'])
            #.sort('idExpedicion', 'Correlativo')
        #.query('match', idExpedicion=64000)

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
            stop['loadProfile'] = float(data['Carga'])
            stop['expandedGetIn'] = float(data['SubidasExpandidas'])
            stop['expandedGetOut'] = float(data['BajadasExpandidas'])
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
        except ESQueryDoesNotHaveParameters as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)


