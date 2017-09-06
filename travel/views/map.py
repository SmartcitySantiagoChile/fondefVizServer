#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
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

    sectors = dict()
    sectors['Lo Barnechea'] = [202, 642]
    sectors['Centro'] = [267, 276, 285, 286]
    sectors['Providencia'] = [175, 176, 179]
    sectors['Las Condes'] = [207, 215, 216]
    sectors['Vitacura'] = [191, 192, 193, 195, 196]
    sectors['Quilicura'] = [557, 831]

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadMapView, self).__init__(es_query_dict)

    def get(self, request):
        self.context['sectors'] = json.dumps(LoadMapView.sectors)
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

        by_zone_agg = A('terms', field='zona_subida', size=1000)

        def add_remaining(es_query, sector, zones):
            es_query.aggs\
                .bucket(sector, A('filter', query.Q('terms', zona_bajada=zones)))\
                .bucket('by_zone', by_zone_agg)\
                .metric('tviaje', 'avg', field='tviaje')\
                .metric('n_etapas', 'avg', field='n_etapas')\
                .metric('distancia_ruta', 'avg', field='distancia_ruta')\
                .metric('distancia_eucl', 'avg', field='distancia_eucl')

        for key in LoadMapView.sectors:
            add_remaining(es_query, key, LoadMapView.sectors[key])

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
