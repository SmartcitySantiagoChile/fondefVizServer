#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search
from errors import ESQueryParametersDoesNotExist, ESQueryDateRangeParametersDoesNotExist, ESQueryResultEmpty
from LoadTravelsGeneric import LoadTravelsGeneric


class LoadTravelsByTravelTimeView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
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
            es_query = self.build_query(request)

            # process ES query
            answer = es_query.execute()

            # self.transformESAnswer(es_query)
            response['travels'] = answer.to_dict()

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

    def build_query(self, request):
        """ create es-query based on params given by user """

        # filtering params
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        day_types = request.GET.getlist('daytypes[]', None)
        periods = request.GET.getlist('periods[]', None)

        # elastic search client
        client = settings.ES_CLIENT_DEVEL
        es_query = Search(using=client, index=LoadTravelsGeneric.INDEX_NAME)

        # common filtering
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

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        # travel time histogram
        es_query.aggs.bucket('tiempos_de_viaje', 'histogram', field='tviaje', interval='15')\
            .metric('cantidad', 'sum', field='factor_expansion')\
            .pipeline('acumulado', 'cumulative_sum', buckets_path='cantidad')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
