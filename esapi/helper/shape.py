# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryOperationProgramDoesNotExist, ESQueryRouteParameterDoesNotExist, \
    ESQueryDateRangeParametersDoesNotExist, ESQueryThereIsMoreThanOneOperationProgram


class ESShapeHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'shape'
        super(ESShapeHelper, self).__init__(index_name)

    def check_operation_program_between_dates(self, auth_route_code, start_date, end_date):
        """
        Check that there is not exist operation program between start date and end date, and if exists it has to be
        equal to start date
        """
        es_query = self.get_base_query().filter('term', route=auth_route_code)
        es_query = es_query.filter('range', startDate={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = es_query.source(['startDate'])
        es_query = es_query[:1000]

        result = es_query.execute()
        days = [x['_source']['date'][:10] for x in result.hits.hits]

        if len(days) == 1:
            if start_date != days[0]:
                raise ESQueryThereIsMoreThanOneOperationProgram(start_date, end_date, days)
        elif len(days) > 0:
            raise ESQueryThereIsMoreThanOneOperationProgram(start_date, end_date, days)

    def get_route_shape(self, auth_route_code, start_date, end_date):

        if not auth_route_code:
            raise ESQueryRouteParameterDoesNotExist()
        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        self.check_operation_program_between_dates(auth_route_code, start_date, end_date)

        es_query = self.get_base_query()
        es_query = es_query.filter('term', route=auth_route_code)
        es_query = es_query.filter('range', startDate={
            'lte': start_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = es_query[:1]
        es_query = es_query.sort('-startDate')

        try:
            point_list = es_query.execute().hist.hits[0].points
        except IndexError:
            # get available days
            es_query = self.get_unique_list_query('startDate', size=1000, query=self.get_base_query())
            available_days = [x.key_as_string[:10] for x in es_query.execute().aggregations.unique.buckets]
            raise ESQueryOperationProgramDoesNotExist(start_date, available_days)

        return point_list
