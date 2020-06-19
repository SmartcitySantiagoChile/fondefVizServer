# -*- coding: utf-8 -*-
from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESOpDataHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'opdata'
        file_extensions = ['opdata']
        super(ESOpDataHelper, self).__init__(index_name, file_extensions)

    def get_route_info(self, op_route, dates):
        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = self.get_base_query()