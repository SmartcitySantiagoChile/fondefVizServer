# -*- coding: utf-8 -*-


from collections import defaultdict

from elasticsearch_dsl import A, Q

from esapi.errors import ESQueryOperatorParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper
from localinfo.helper import get_operator_list_for_select_input
from functools import reduce


class ESBipHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "bip"
        file_extensions = ['bip']
        super(ESBipHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self):
        return self._get_available_days('validationTime')

    def get_bip_by_operator_data(self, dates, valid_operator_list):

        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist
        operator_list = get_operator_list_for_select_input(filter=valid_operator_list)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q("range", validationTime={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        aggs = A('date_histogram', field='validationTime', interval='day')
        es_query.aggs.bucket('histogram', aggs).\
            bucket('operators', 'terms', field='operator', size=1000)

        return es_query, operator_list
