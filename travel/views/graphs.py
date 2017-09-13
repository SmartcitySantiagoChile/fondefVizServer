#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse

from errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)
from .generic import LoadTravelsGeneric, GetDataGeneric


class LoadGraphsView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadGraphsView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/graphs.html", self.context)


class GetGraphsData(GetDataGeneric):

    def __init__(self):
        super(GetGraphsData, self).__init__()

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
            # es_query_dict['table'] = self.build_table_query(request)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        # execute es queries and return as JSON
        response.update(self.execute_queries(es_query_dict))
        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: queries
    # ========================================================

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
