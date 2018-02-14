# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryResultEmpty, ESQueryExistTwoShapesInTimePeriod


class ESShapeHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'shape'
        super(ESShapeHelper, self).__init__(index_name)

    def get_route_shape(self, route, start_date, end_date):

        es_query = self.get_base_query()
        es_query = es_query.filter('term', route=route)
        es_query = es_query.filter('range', startDate={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })

        if es_query.execute().hits.total != 0:
            raise ESQueryExistTwoShapesInTimePeriod()

        es_query = self.get_base_query()
        es_query = es_query.filter('term', route=route)
        es_query = es_query.filter('range', startDate={
            'lte': start_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = es_query.sort('-startDate')

        r = es_query.execute()

        if r.hits.total == 0:
            raise ESQueryResultEmpty()

        return (r.hits[0].points)
