# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        super(ESStopHelper, self).__init__(index_name)

    def get_stop_list(self, auth_route_code, day, flat=False,
                      fields=('userStopCode', 'authStopCode', 'stopName', 'latitude', 'longitude', 'order')):
        """ ask to elasticsearch for a match values """

        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        if day:
            es_query = es_query.filter('range', date={
                'gte': day,
                'lte': day,
                'format': 'yyyy-MM-dd'})

        # there is not route with more than 500 stops
        es_query = es_query[:500]
        es_query = es_query.sort('order')
        es_query = es_query.source(fields)

        stop_list = [stop.to_dict() for stop in es_query.execute()]

        if flat:
            # assume that dict has just one attribute
            key = stop_list[0].keys()[0]
            stop_list = [dict_obj[key] for dict_obj in stop_list]

        return stop_list
