#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from django.shortcuts import render
from django.http import JsonResponse

from elasticsearch_dsl import A, query
from esapi.errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)
from .generic import LoadTravelsGeneric, GetDataGeneric


class LoadMapView(LoadTravelsGeneric):

    # zonas 777 para cada sector
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


class GetMapData(GetDataGeneric):

    def __init__(self):
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
            es_query_dict['map'] = self.build_map_query(request)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        # execute es queries and return as JSON
        response.update(self.execute_queries(es_query_dict))
        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: queries
    # ========================================================

    def build_map_query(self, request):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request)

        # obs: by using size=1000, we assume there are less than '1000' zones
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
