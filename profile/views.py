from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
# Create your views here.

class LoadProfileByExpeditionView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}

    def get(self, request):
        template = "profile/expedition.html"

        return render(request, template, self.context)


class GetLoadProfileByExpeditionData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def get(self, request):
        ''' expedition data '''
        expeditionId = request.GET.get('idExpedition','')

        client = Elasticsearch("172.17.57.47:9200")
        s = Search(using=client, index="profiles")\
            .query('match', idExpedicion=expeditionId)\
            .query('match', Cumplimiento='C')\
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada', 'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin'])\
            .sort('idExpedicion', 'Correlativo')
        #.query('match', idExpedicion=64000)
 
        response = {}
        # debug
        #response['query'] = s.to_dict()
        #response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        response['trips'] = {}
        for hit in s.scan():
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
            stop['distOnRoute'] = data['DistEnRuta']
            stop['time'] = data['Tiempo']
            stop['order'] = int(data['Correlativo'])
            stop['loadProfile'] = float(data['Carga'])
            stop['expandedGetIn'] = float(data['BajadasExpandidas'])
            stop['expandedGetOut'] = float(data['SubidasExpandidas'])
            response['trips'][expeditionId]['stops'].append(stop)

        for expeditionId in response['trips']:
            response['trips'][expeditionId]['stops'] = sorted(response['trips'][expeditionId]['stops'], 
                 key=lambda record: record['order'])

        return JsonResponse(response, safe=False)

















