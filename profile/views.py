from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
# Create your views here.

from localinfo.models import TimePeriod

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

    def makeQuery(self, request):
        ''' create es-query based on params given by user '''

        fromDate = request.GET.get('from', None)
        toDate = request.GET.get('to', None)
        route = request.GET.get('route', None)
        licensePlate = request.GET.getlist('licensePlate', None)
        dayType = request.GET.getlist('dayType', None)
        period = request.GET.getlist('period', None)

        # get list of profile*
        client = Elasticsearch("172.17.57.47:9200")
        esQuery = Search(using=client, index="profiles")

        if route:
            esQuery = esQuery.query('match_phrase', ServicioSentido=route)
        if licensePlate:
            esQuery = esQuery.query('match', Patente=' '.join(licensePlate))
        if dayType:
            esQuery = esQuery.query('match', TipoDia=' '.join(dayType))
        if period:
            esQuery = esQuery.query('match', Periodo=' '.join(period))
            
        esQuery = esQuery.query('match', Cumplimiento='C')\
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada', 'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero'])
            #.sort('idExpedicion', 'Correlativo')
        #.query('match', idExpedicion=64000)

        return esQuery
 
    def get(self, request):
        ''' expedition data '''

        esQuery = self.makeQuery(request)

        response = {}
        # debug
        response['query'] = esQuery.to_dict()
        #response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        response['trips'] = {}
        for hit in esQuery.scan():
            data = hit.to_dict()

            expeditionId = data['idExpedicion']
            if expeditionId not in response['trips']:
                response['trips'][expeditionId] = {'info': {}, 'stops': []}

            response['trips'][expeditionId]['info']['capacity'] = int(data['Capacidad'])
            response['trips'][expeditionId]['info']['licensePlate'] = data['Patente']
            response['trips'][expeditionId]['info']['route'] = data['ServicioSentido']
            response['trips'][expeditionId]['info']['timeTripInit'] = data['Hini']
            response['trips'][expeditionId]['info']['timeTripEnd'] = data['Hfin']
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
            response['trips'][expeditionId]['stops'].append(stop)

        for expeditionId in response['trips']:
            response['trips'][expeditionId]['stops'] = sorted(response['trips'][expeditionId]['stops'], 
                 key=lambda record: record['order'])

        return JsonResponse(response, safe=False)

















