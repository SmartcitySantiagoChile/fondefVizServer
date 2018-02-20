# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools
from django.shortcuts import render
from django.http import JsonResponse

from elasticsearch_dsl import A, Q
from esapi.errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty,
    ESQueryOriginZoneParameterDoesNotExist,
    ESQueryDestinationZoneParameterDoesNotExist
)
from django.views.generic import View
from .generic import LoadTravelsGeneric, GetDataGeneric


class LoadStrategiesView(LoadTravelsGeneric):

    def __init__(self):
        """"""
        es_query_dict = dict()
        super(LoadStrategiesView, self).__init__(es_query_dict)

    def get(self, request):
        return render(request, "travel/strategies.html", self.context)


class GetStrategiesData(GetDataGeneric):

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
            es_query_dict = self.build_strategies_travels(request, False)
            strategies_tuples = dict()
            for hit in es_query_dict.scan():
                _data = hit.to_dict()
                t = ''
                if _data['tipo_transporte_1'] == 2:
                    t += 'METRO'
                elif _data['tipo_transporte_1'] == 4:
                    t += 'METROTREN'
                else:
                    t += _data['srv_1']
                t += " | "

                if _data['tipo_transporte_2'] == 2:
                    t += 'METRO'
                elif _data['tipo_transporte_2'] == 4:
                    t += 'METROTREN'
                else:
                    t += _data['srv_2']
                t += " | "

                if _data['tipo_transporte_3'] == 2:
                    t += 'METRO'
                elif _data['tipo_transporte_3'] == 4:
                    t += 'METROTREN'
                else:
                    t += _data['srv_3']
                t += " | "

                if _data['tipo_transporte_4'] == 2:
                    t += 'METRO'
                elif _data['tipo_transporte_4'] == 4:
                    t += 'METROTREN'
                else:
                    t += _data['srv_4']

                if t not in strategies_tuples:
                    strategies_tuples[t] = {'travels': []}
                strategies_tuples[t]['travels'].append(_data['id'])

            response['strategies'] = strategies_tuples
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty,
                ESQueryOriginZoneParameterDoesNotExist, ESQueryDestinationZoneParameterDoesNotExist) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)

    # ========================================================
    # Supporting methods: queries
    # ========================================================

    def build_strategies_travels(self, request, multiquery=True):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.build_base_query(request, multiquery)
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

        origin_zone = request.GET.getlist('origin[]', None)
        if not origin_zone:
            raise ESQueryOriginZoneParameterDoesNotExist()

        destination_zone = request.GET.getlist('destination[]', None)
        if not destination_zone:
            raise ESQueryDestinationZoneParameterDoesNotExist()

        # return the hits, ES can't process data as we want
        return es_query
