#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import JsonResponse

from esapi.errors import (
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
            es_query_dict['indicators'] = self.build_indicators_query(request)
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

        def add_histogram(es_query, field, interval, bmin, bmax):
            es_query.aggs.bucket(
                    field,
                    'histogram',
                    field=field,
                    interval=interval,
                    min_doc_count=0,
                    extended_bounds={'min': bmin, 'max': bmax}
                )\
                .metric('bin', 'sum', field='factor_expansion')\
                .pipeline('total', 'cumulative_sum', buckets_path='bin')

        # up to 120 min
        add_histogram(es_query, 'tviaje', '15', 0, 120)

        # at least from 1 to 5 etapas
        add_histogram(es_query, 'n_etapas', '1', 1, 5)

        # distances are this values right?
        add_histogram(es_query, 'distancia_ruta', '5000', 0, 30000)
        add_histogram(es_query, 'distancia_eucl', '5000', 0, 30000)

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]

    def build_indicators_query(self, request):
        """
        """
        es_query = self.build_base_query(request)
        es_query.aggs.metric('documentos', 'value_count', field='id')
        es_query.aggs.metric('viajes', 'sum', field='factor_expansion')
        es_query.aggs.metric('tviaje', 'stats', field='tviaje')
        es_query.aggs.metric('n_etapas', 'stats', field='n_etapas')
        es_query.aggs.metric('distancia_ruta', 'stats', field='distancia_ruta')
        es_query.aggs.metric('distancia_eucl', 'stats', field='distancia_eucl')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return es_query[:0]
