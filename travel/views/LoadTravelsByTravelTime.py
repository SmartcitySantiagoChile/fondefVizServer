#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, A
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from LoadTravelsGeneric import LoadTravelsGeneric


class LoadTravelsByTravelTimeView(LoadTravelsGeneric):
    """"""

    def __init__(self):
        """"""
        # es_route_query = Search()
        # es_route_query = es_route_query[:0]
        # aggs = A('terms', field="ServicioSentido", size=1000)
        # es_route_query.aggs.bucket('unique', aggs)
        #
        es_query_dict = dict()
        # es_query_dict['routes'] = es_route_query

        super(LoadTravelsByTravelTimeView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/byTravelTime.html", self.context)


class GetLoadTravelsByTravelTimeData(View):
    """"""

    def __init__(self):
        """"""
        self.context = {}
        super(GetLoadTravelsByTravelTimeData, self).__init__()

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        route = request.GET.get('route', None)
        license_plate = request.GET.getlist('licensePlate[]', None)
        day_type = request.GET.getlist('dayType[]', None)
        period = request.GET.getlist('period[]', None)
        expedition_id = request.GET.getlist('expeditionId[]', None)

        # get list of profile
        client = settings.ES_CLIENT_DEVEL
        es_query = Search(using=client, index=LoadTravelsGeneric.INDEX_NAME)

        exists_parameters = False
        if expedition_id:
            es_query = es_query.filter('terms', idExpedicion=expedition_id)
            exists_parameters = True

        if route:
            es_query = es_query.filter('term', ServicioSentido=route)
            exists_parameters = True
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if license_plate:
            es_query = es_query.filter('terms', Patente=license_plate)
            exists_parameters = True

        if day_type:
            es_query = es_query.filter('terms', TipoDia=day_type)
            exists_parameters = True

        if period:
            es_query = es_query.filter('terms', PeriodoTSExpedicion=period)
            exists_parameters = True

        if not exists_parameters:
            raise ESQueryParametersDoesNotExist()

        es_query = es_query.filter('term', Cumplimiento='C') \
            .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada',
                     'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero',
                     'ParaderoUsuario', 'PeriodoTSExpedicion', 'TipoDia', 'PeriodoTSParada'])

        return es_query

    def cleanData(self, data):
        """ round to zero values between [-1, 0] """
        value = float(data)
        if -1.0 < value and value < 0.0:
            return 0
        return value

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        trips = {}

        for hit in esQuery.scan():
            data = hit.to_dict()

            expedition_id = data['idExpedicion']
            if expedition_id not in trips:
                trips[expedition_id] = {'info': {}, 'stops': []}

            trips[expedition_id]['info']['capacity'] = int(data['Capacidad'])
            trips[expedition_id]['info']['licensePlate'] = data['Patente']
            trips[expedition_id]['info']['route'] = data['ServicioSentido']
            trips[expedition_id]['info']['timeTripInit'] = data['Hini']
            trips[expedition_id]['info']['authTimePeriod'] = data['PeriodoTSExpedicion']
            trips[expedition_id]['info']['timeTripEnd'] = data['Hfin']
            trips[expedition_id]['info']['dayType'] = data['TipoDia']
            stop = dict()
            stop['name'] = data['NombreParada']
            stop['authStopCode'] = data['Paradero']
            stop['userStopCode'] = data['ParaderoUsuario']
            stop['authTimePeriod'] = data['PeriodoTSParada']
            stop['distOnPath'] = data['DistEnRuta']
            stop['stopTime'] = data['Tiempo']
            stop['order'] = int(data['Correlativo'])

            # to avoid movement of distribution chart
            stop['loadProfile'] = self.cleanData(data['Carga'])
            stop['expandedGetIn'] = self.cleanData(data['SubidasExpandidas'])
            stop['expandedGetOut'] = self.cleanData(data['BajadasExpandidas'])
            trips[expedition_id]['stops'].append(stop)

        for expedition_id in trips:
            trips[expedition_id]['stops'] = sorted(trips[expedition_id]['stops'],
                                                   key=lambda record: record['order'])

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips

    def get(self, request):
        """ expedition data """
        response = dict()
        response['trips'] = dict()

        try:
            es_query = self.buildQuery(request)
            response['trips'] = self.transformESAnswer(es_query)
            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)
