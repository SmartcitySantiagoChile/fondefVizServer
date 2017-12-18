#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse

from elasticsearch_dsl import A, Q
from errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)
from django.views.generic import View
from .generic import LoadTravelsGeneric, GetDataGeneric

class LoadFromToMapsView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadFromToMapsView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/from_to.html", self.context)


class GetFromToMapsData(GetDataGeneric):

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
            es_query_dict['origin_zone'] = self.build_origin_travels(request)
            es_query_dict['destination_zone'] = self.build_destination_travels(request)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        # execute es queries and return as JSON
        response.update(self.execute_queries(es_query_dict))
        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: queries
    # ========================================================

    def build_origin_travels(self, request):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)
        print(request);

        # 4 or more etapas
        n_etapas = request.GET.getlist('n_etapas[]', None)
        if n_etapas:
            if "5+" in n_etapas:
                n_etapas.remove("5+")
                es_query = es_query.query(
                    Q('terms', n_etapas=n_etapas) |
                    Q('range', n_etapas={'gte': 5})
                )
            else:
                es_query = es_query.filter('terms', n_etapas=n_etapas)

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_subida', size=1000)

        # required stats
        es_query.aggs\
            .bucket('by_zone', by_zone_agg)\
            .metric('tviaje', 'avg', field='tviaje')\
            .metric('n_etapas', 'avg', field='n_etapas')\
            .metric('distancia_ruta', 'avg', field='distancia_ruta')\
            .metric('distancia_eucl', 'avg', field='distancia_eucl')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]

    def build_destination_travels(self, request):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # 4 or more etapas
        n_etapas = request.GET.getlist('n_etapas[]', None)
        if n_etapas:
            if "5+" in n_etapas:
                n_etapas.remove("5+")
                es_query = es_query.query(
                    Q('terms', n_etapas=n_etapas) |
                    Q('range', n_etapas={'gte': 5})
                )
            else:
                es_query = es_query.filter('terms', n_etapas=n_etapas)

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_bajada', size=1000)

        # required stats
        es_query.aggs\
            .bucket('by_zone', by_zone_agg)\
            .metric('tviaje', 'avg', field='tviaje')\
            .metric('n_etapas', 'avg', field='n_etapas')\
            .metric('distancia_ruta', 'avg', field='distancia_ruta')\
            .metric('distancia_eucl', 'avg', field='distancia_eucl')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
