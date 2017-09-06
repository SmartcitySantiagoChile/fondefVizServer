#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, MultiSearch, A, query
from errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)
from .generic import LoadTravelsGeneric


class LoadMapView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadMapView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/map.html", self.context)


class GetMapData(View):

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
        self.client = settings.ES_CLIENT_DEVEL

        self.context = {}
        super(GetMapData, self).__init__()

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

        # build es multisearch dictionary
        es_query_dict = dict()
        try:
            es_query_dict['histogram'] = self.build_histogram_query(request)
            es_query_dict['map'] = self.build_map_query(request)
            # es_query_dict['table'] = self.build_table_query(request)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        # execute es queries and return as JSON
        response.update(self.execute_queries(es_query_dict))
        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: query execution
    # ========================================================

    def execute_queries(self, es_query_dict):
        """
        performs an ES multisearch to execute all queries at once
        """
        result = dict()

        multisearch = MultiSearch(using=self.client, index=LoadTravelsGeneric.INDEX_NAME)

        # build multisearch
        names = list()
        for query_name, es_query in es_query_dict.iteritems():
            multisearch = multisearch.add(es_query)
            names.append(query_name)

            # append debug information
            if settings.DEBUG:
                result[query_name + '_query'] = es_query.to_dict()

        # execute and parse results
        try:
            # use this to see the generated query
            # >>> print multisearch.to_dict()
            answers = multisearch.execute()

            for index, answer in enumerate(answers):
                name = names[index]
                result[name] = answer.to_dict()

                # append debug information
                if settings.DEBUG:
                    result[name + '_state'] = {
                        'success': answer.success(),
                        'took': answer.took,
                        'total': answer.hits.total
                    }

        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            result['status'] = e.getStatusResponse()

        return result

    # ========================================================
    # Supporting methods: queries
    # ========================================================

    def build_base_query(self, request):
        """
        TODO: realizar filtrado sólo 1 vez y no por cada query

        raises ESQueryResultEmpty ?
        raises ESQueryParametersDoesNotExist ?
        raises ESQueryDateRangeParametersDoesNotExist
        """
        es_query = Search()

        # filtering params
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)
        day_types = request.GET.getlist('daytypes[]', None)
        periods = request.GET.getlist('periods[]', None)

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

        return es_query

    def build_histogram_query(self, request):
        """
        Builds a elastic search query for the travels histogram
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # travel time histogram (15 min buckets)
        es_query.aggs.bucket('tiempos_de_viaje', 'histogram', field='tviaje', interval='15')\
            .metric('cantidad', 'sum', field='factor_expansion')\
            .pipeline('acumulado', 'cumulative_sum', buckets_path='cantidad')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]

    def build_table_query(self, request):
        """
        Builds a elastic search query for the travels table
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]

    def build_map_query(self, request):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # travel time map

        by_zone_agg = A('terms', field='zona_subida', size=1000)

        zones_las_condes = [287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323]
        zones_lo_barnechea = [324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336]
        zones_providencia = [494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516]
        zones_santiago = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52]
        zones_colina = [746, 740]

        def add_remaining(es_query, sector, zones):
            es_query.aggs\
                .bucket(sector, A('filter', query.Q('terms', zona_bajada=zones)))\
                .bucket('by_zone', by_zone_agg)\
                .metric('tviaje', 'avg', field='tviaje')\
                .metric('n_etapas', 'avg', field='n_etapas')\
                .metric('distancia_ruta', 'avg', field='distancia_ruta')\
                .metric('distancia_eucl', 'avg', field='distancia_eucl')

        add_remaining(es_query, 'LAS CONDES', zones_las_condes)
        add_remaining(es_query, 'LO BARNECHEA', zones_lo_barnechea)
        add_remaining(es_query, 'PROVIDENCIA', zones_providencia)
        add_remaining(es_query, 'SANTIAGO', zones_santiago)
        add_remaining(es_query, 'COLINA', zones_colina)

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
