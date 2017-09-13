#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse

from elasticsearch_dsl import A, query
from errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)
from .generic import LoadTravelsGeneric, GetDataGeneric


class LoadLargeTravelsView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadLargeTravelsView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/large.html", self.context)


class GetLargeTravelsData(GetDataGeneric):

    def __init__(self):
        super(GetDataGeneric, self).__init__()

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
            es_query_dict['large'] = self.build_large_travels_query(request)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        # execute es queries and return as JSON
        response.update(self.execute_queries(es_query_dict))
        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: queries
    # ========================================================

    def build_large_travels_query(self, request):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # 4 or more etapas
        es_query = es_query.filter('range', n_etapas={'gte': 4})

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_subida', size=1000)

        # required stats
        es_query.aggs\
            .bucket('by_zone', by_zone_agg)\
            .metric('tviaje', 'avg', field='tviaje')\
            .metric('n_etapas', 'stats', field='n_etapas')\
            .metric('distancia_ruta', 'avg', field='distancia_ruta')\
            .metric('distancia_eucl', 'avg', field='distancia_eucl')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
