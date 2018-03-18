# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryOperationProgramDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryThereIsMoreThanOneOperationProgram, ESQueryRouteParameterDoesNotExist, ESQueryStopListDoesNotExist


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        super(ESStopHelper, self).__init__(index_name)

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

        return dates[0]

    def get_stop_list(self, auth_route_code, start_date, end_date):
        """ ask to elasticsearch for a match values """

        if not auth_route_code:
            raise ESQueryRouteParameterDoesNotExist()
        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        es_query = es_query.filter('range', startDate={
            'lte': start_date,
            'format': 'yyyy-MM-dd'
        }).sort('-startDate')[:1]

        try:
            stop_list = es_query.execute().hits.hits[0]['_source']['stops']
        except IndexError:
            raise ESQueryStopListDoesNotExist()

        return stop_list

    def get_available_days(self):
        return self._get_available_days('startDate', [])

    def get_route_list(self):
        searches = {
            "days": self.get_unique_list_query('authRouteCode', size=5000)
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result
