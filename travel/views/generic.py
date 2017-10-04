#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from django.views.generic import View
from django.core.serializers import serialize
from django.conf import settings

from localinfo.models import TimePeriod, Commune, HalfHour

from elasticsearch_dsl import Search, MultiSearch
from errors import (
    ESQueryParametersDoesNotExist,
    ESQueryDateRangeParametersDoesNotExist,
    ESQueryResultEmpty
)


class LoadTravelsGeneric(View):
    """ generic view to load profile data """

    # elastic search index name
    INDEX_NAME = "travel"

    def __init__(self, additional_es_query_dict):
        self.context = dict()
        self.context.update(self.get_local_info_dict())
        super(LoadTravelsGeneric, self).__init__()

    def get_local_info_dict(self):
        communes = Commune.objects.all()
        halfhours = HalfHour.objects.all()
        timeperiods = TimePeriod.objects.all()

        day_types = list()
        day_types.append({'pk': 0, 'name': 'Laboral'})
        day_types.append({'pk': 1, 'name': 'Sábado'})
        day_types.append({'pk': 2, 'name': 'Domingo'})

        data = dict()
        data['daytypes'] = json.dumps(day_types)
        data['communes'] = serialize('json', communes)
        data['halfhours'] = serialize('json', halfhours)
        data['timeperiods'] = serialize('json', timeperiods)
        return data


class GetDataGeneric(View):

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

    # ========================================================
    # Supporting methods: query execution
    # ========================================================

    def execute_queries(self, es_query_dict):
        """
        performs an ES multisearch to execute all queries at once
        """
        result = dict()

        multisearch = MultiSearch(using=settings.ES_CLIENT, index=LoadTravelsGeneric.INDEX_NAME)

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
