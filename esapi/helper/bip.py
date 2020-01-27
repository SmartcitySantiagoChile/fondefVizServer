# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import A

from esapi.errors import ESQueryOperatorParameterDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper
from localinfo.helper import get_operator_list_for_select_input


class ESBipHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "bip"
        file_extensions = ['bip']
        super(ESBipHelper, self).__init__(index_name, file_extensions)


    def get_available_days(self, valid_operator_list):
        return self._get_available_days('expeditionStartTime', valid_operator_list)

    def get_available_routes(self, valid_operator_list):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        aggs = A('terms', field="route", size=5000)
        es_query.aggs.bucket('route', aggs)
        es_query.aggs['route']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['operator', 'userRoute'])

        operator_list = get_operator_list_for_select_input(filter=valid_operator_list)

        result = defaultdict(lambda: defaultdict(list))
        for hit in es_query.execute().aggregations.route.buckets:
            data = hit.to_dict()
            auth_route = data['key']
            operator_id = data['additionalInfo']['hits']['hits'][0]['_source']['operator']
            user_route = data['additionalInfo']['hits']['hits'][0]['_source']['userRoute']

            result[operator_id][user_route].append(auth_route)

        return result, operator_list


