# -*- coding: utf-8 -*-


from functools import reduce

from elasticsearch_dsl import Q

from esapi.errors import ESQueryOperationProgramDoesNotExist, ESQueryRouteParameterDoesNotExist, \
    ESQueryDateRangeParametersDoesNotExist, ESQueryThereIsMoreThanOneOperationProgram, ESQueryShapeDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESShapeHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'shape'
        file_extensions = ['shape']
        super(ESShapeHelper, self).__init__(index_name, file_extensions)

    def check_operation_program_between_dates(self, start_date, end_date):
        """
        Check that there is not exist operation program between start date and end date, and if exists it has to be
        equal to start date

        :param start_date: lower date bound
        :param end_date: upper date bound
        :return: None
        """
        es_query = self.get_base_query().filter('range', startDate={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = self.get_unique_list_query("startDate", size=5000, query=es_query)
        dates = [x.key_as_string[:10] for x in es_query.execute().aggregations.unique.buckets]
        days_quantity = len(dates)

        if days_quantity == 0:
            # check if there is operation program previous to start_Date
            es_query = self.get_base_query().filter('range', startDate={
                'lt': start_date,
                'format': 'yyyy-MM-dd'
            })
            es_query = self.get_unique_list_query("startDate", size=5000, query=es_query)
            if len(es_query.execute().aggregations.unique.buckets) == 0:
                raise ESQueryOperationProgramDoesNotExist(start_date, end_date)
        elif days_quantity > 1 or (days_quantity == 1 and start_date != dates[0]):
            raise ESQueryThereIsMoreThanOneOperationProgram(start_date, end_date, dates)

    def get_most_recent_operation_program_date(self, asked_date):
        """
        :param asked_date: date with format yyyy-MM-dd
        :return: date with most recen operation program:
        """

        # check if there is operation program previous to start_Date
        es_query = self.get_base_query().filter('range', startDate={
            'lte': asked_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = self.get_unique_list_query("startDate", size=5000, query=es_query)
        dates = es_query.execute().aggregations.unique.buckets
        if len(dates) == 0:
            raise ESQueryOperationProgramDoesNotExist(asked_date)

        return dates[0].key_as_string[:10]

    def get_route_shape(self, auth_route_code, dates):
        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        if not auth_route_code:
            raise ESQueryRouteParameterDoesNotExist()

        es_query = self.get_base_query()
        es_query = es_query.filter('term', authRouteCode=auth_route_code)
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            filter_q = Q('range', startDate={
                'lte': start_date,
                'format': 'yyyy-MM-dd'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter]).sort('-startDate')[:1]
        try:
            point_list = es_query.execute().hits.hits[0]['_source']
        except IndexError:
            raise ESQueryShapeDoesNotExist()

        return point_list

    def get_available_days(self):
        return self._get_available_days('startDate', [])

    def get_route_list(self):
        query = self.get_unique_list_query('authRouteCode', size=5000)
        result = self.get_attr_list(self.make_multisearch_query_for_aggs(query, flat=True), 'unique')

        return result
