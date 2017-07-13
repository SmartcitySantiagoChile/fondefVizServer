#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.views.generic import View
from django.conf import settings
from django.core.serializers import serialize

from elasticsearch_dsl import Search, A, MultiSearch
from localinfo.models import TimePeriod, Commune, HalfHour


class LoadTravelsGeneric(View):
    """ generic view to load profile data """

    # elastic search index name
    INDEX_NAME = "travel"

    def __init__(self, additionalESQueryDict):
        """ contructor """
        # es_query_dict = self.getDefaultESQueryDict()
        # es_query_dict.update(additionalESQueryDict)

        # self.context = self.getESQueryResult(es_query_dict)
        self.context = self.getLocalInfoDict()
        super(LoadTravelsGeneric, self).__init__()


    def getLocalInfoDict(self):
        communes = Commune.objects.all()
        halfhours = HalfHour.objects.all()
        timeperiods = TimePeriod.objects.all()

        day_types = list()
        day_types.append({'pk': 0, 'name': 'Laboral'})
        day_types.append({'pk': 1, 'name': 'Sábado'})
        day_types.append({'pk': 2, 'name': 'Domingo'})

        data = dict()
        data['daytypes'] = day_types
        data['communes'] = communes
        data['halfhours'] = halfhours
        data['timeperiods'] = serialize('json', timeperiods)
        return data

    def getESQueryResult(self, esQueryDict):
        """ retrieve all data available in elastic search """
        client = settings.ES_CLIENT_DEVEL

        multi_search = MultiSearch(using=client, index=self.INDEX_NAME)

        keys = []
        for key, es_query in esQueryDict.iteritems():
            multi_search = multi_search.add(es_query)
            keys.append(key)

        # to see the query generated
        # print multiSearch.to_dict()
        responses = multi_search.execute()

        result = {}
        for index, response in enumerate(responses):
            result_list = []
            for tag in response.aggregations.unique.buckets:
                result_list.append(tag.key)
            result_list.sort()

            result[keys[index]] = result_list

        return result

    def getDefaultESQueryDict(self):
        """ create a dict of elastic search query """

        es_time_period_query = Search()
        es_time_period_query = es_time_period_query[:0]
        aggs = A('terms', field="PeriodoTSExpedicion", size=50)
        es_time_period_query.aggs.bucket('unique', aggs)

        es_day_type_query = Search()
        es_day_type_query = es_day_type_query[:0]
        aggs = A('terms', field="TipoDia", size=10)
        es_day_type_query.aggs.bucket('unique', aggs)

        result = dict()
        result['periods'] = es_time_period_query
        result['dayTypes'] = es_day_type_query

        return result
