#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, A
from errors import ESQueryParametersDoesNotExist, ESQueryDateRangeParametersDoesNotExist, ESQueryResultEmpty
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


    def __init__(self):

        self.default_fields = [
            'tviaje',
            'n_etapas',
            'factor_expansion',
            'comuna_subida',
            'comuna_bajada',
            'zona_subida',
            'zona_bajada'
        ]

        self.context = {}
        super(GetLoadTravelsByTravelTimeData, self).__init__()


    # ========================================================
    # View Interface
    # ========================================================
    # only 'get' method

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.

        The response is a Json document.
        """
        response = dict()
        response['travels'] = dict()

        try:
            # build elastic search query, based on the requested filtering options
            es_query = self.buildQuery(request)

            # process ES query
            answer = es_query.execute()

            # self.transformESAnswer(es_query)
            # response['travels'] = answer.to_dict()

            # append debug information
            if settings.DEBUG:
                response['query'] = es_query.to_dict()
                response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}

        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods
    # ========================================================

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        # filtering params
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        day_types = request.GET.getlist('daytype', None)
        periods = request.GET.getlist('period', None)

        # elastic search client
        client = settings.ES_CLIENT_DEVEL
        es_query = Search(using=client, index=LoadTravelsGeneric.INDEX_NAME)

        if from_date and to_date:
            es_query = es_query.filter(
                'range',
                tiempo_subida={
                    'gte': from_date + ' 00:00',
                    'lte': to_date + ' 23:59',
                    'format': 'dd/MM/yyyy HH:mm',
                    'time_zone': 'America/Santiago'
                })
        else:
            # this query requires both fields!
            raise ESQueryDateRangeParametersDoesNotExist()



        exists_parameters = True
        # if day_types:
        #     es_query = es_query.filter('terms', tipodia=day_type)
        #     exists_parameters = True
        #
        # if periods:
        #     es_query = es_query.filter('terms', periodo_subida=period)
        #     exists_parameters = True

        # from date: 13/07/2017
        # to   date: 13/07/2017
        # day
        # types: 0, 2
        # periods: 1, 5



        if not exists_parameters:
            raise ESQueryParametersDoesNotExist()

        # es_query = es_query.filter('term', Cumplimiento='C') \
        #     .source(['Capacidad', 'Tiempo', 'Patente', 'ServicioSentido', 'Carga', 'idExpedicion', 'NombreParada',
        #              'BajadasExpandidas', 'SubidasExpandidas', 'Correlativo', 'DistEnRuta', 'Hini', 'Hfin', 'Paradero',
        #              'ParaderoUsuario', 'PeriodoTSExpedicion', 'TipoDia', 'PeriodoTSParada'])
        return es_query.source(self.default_fields)

    def cleanData(self, data):
        """ round to zero values between [-1, 0] """
        value = float(data)
        if -1.0 < value and value < 0.0:
            return 0
        return value

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        travels = {}

        count = 0
        for hit in esQuery.scan():
            data = hit.to_dict()
            count += 1
            # expedition_id = data['idExpedicion']
            # if expedition_id not in trips:
            #     trips[expedition_id] = {'info': {}, 'stops': []}
            #
            # trips[expedition_id]['info']['capacity'] = int(data['Capacidad'])
            # trips[expedition_id]['info']['licensePlate'] = data['Patente']
            # trips[expedition_id]['info']['route'] = data['ServicioSentido']
            # trips[expedition_id]['info']['timeTripInit'] = data['Hini']
            # trips[expedition_id]['info']['authTimePeriod'] = data['PeriodoTSExpedicion']
            # trips[expedition_id]['info']['timeTripEnd'] = data['Hfin']
            # trips[expedition_id]['info']['dayType'] = data['TipoDia']
            # stop = dict()
            # stop['name'] = data['NombreParada']
            # stop['authStopCode'] = data['Paradero']
            # stop['userStopCode'] = data['ParaderoUsuario']
            # stop['authTimePeriod'] = data['PeriodoTSParada']
            # stop['distOnPath'] = data['DistEnRuta']
            # stop['stopTime'] = data['Tiempo']
            # stop['order'] = int(data['Correlativo'])
            #
            # # to avoid movement of distribution chart
            # stop['loadProfile'] = self.cleanData(data['Carga'])
            # stop['expandedGetIn'] = self.cleanData(data['SubidasExpandidas'])
            # stop['expandedGetOut'] = self.cleanData(data['BajadasExpandidas'])
            # trips[expedition_id]['stops'].append(stop)
            pass

        # for expedition_id in trips:
        #     trips[expedition_id]['stops'] = sorted(trips[expedition_id]['stops'],
        #                                            key=lambda record: record['order'])

        travels['count'] = count
        if not travels.keys():
            raise ESQueryResultEmpty()

        return travels
