# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryStopListDoesNotExist, ESQueryStartDateParameterDoesNotExist, \
    ESQueryEndDateParameterDoesNotExist, ESQueryThereIsMoreThanOneStopList, ESQueryRouteParameterDoesNotExist


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        super(ESStopHelper, self).__init__(index_name)

    def check_operation_program_between_dates(self, auth_route_code, start_date, end_date):
        """
        Check that there is not exist operation program between start date and end date, and if exists it has to be
        equal to start date
        """
        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        es_query = es_query.filter('range', date={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = es_query.source(['date'])
        es_query = es_query[:1000]

        result = es_query.execute()
        days = [x['_source']['date'][:10] for x in result.hits.hits]

        if len(days) == 1:
            if start_date != days[0]:
                raise ESQueryThereIsMoreThanOneStopList(start_date, end_date, days)
        elif len(days) > 0:
            raise ESQueryThereIsMoreThanOneStopList(start_date, end_date, days)

    def get_stop_list(self, auth_route_code, start_date, end_date):
        """ ask to elasticsearch for a match values """

        if not auth_route_code:
            raise ESQueryRouteParameterDoesNotExist()
        if not start_date:
            raise ESQueryStartDateParameterDoesNotExist()
        if not end_date:
            raise ESQueryEndDateParameterDoesNotExist()

        self.check_operation_program_between_dates(auth_route_code, start_date, end_date)

        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        es_query = es_query.filter('range', date={
            'lte': start_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = es_query[:1]
        es_query = es_query.sort('-date')

        try:
            stop_list = es_query.execute().hits.hits[0]['_source']['stops']
        except IndexError:
            # get available days
            es_query = self.get_unique_list_query('date', size=1000, query=self.get_base_query())
            available_days = [x.key_as_string[:10] for x in es_query.execute().aggregations.unique.buckets]
            raise ESQueryStopListDoesNotExist(start_date, available_days)

        return stop_list
