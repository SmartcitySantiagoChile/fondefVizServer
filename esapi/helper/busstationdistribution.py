# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESBusStationDistributionHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "busstationdistribution"
        file_extensions = ['busstationdistribution']
        super(ESBusStationDistributionHelper, self).__init__(index_name, file_extensions)

    def get_data(self, start_date, end_date, day_type):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        es_query = es_query.filter("range", date={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        # omit hits
        es_query = es_query[:0]

        es_query.aggs \
            .bucket('by_bus_station_id', 'terms', field='busStationId') \
            .bucket('by_bus_station_name', 'terms', field='busStationName') \
            .bucket('by_assignation', 'terms', field='assignation') \
            .bucket('by_operator', 'terms', field='operator') \
            .metric('total', 'sum', field='total') \
            .metric('sum', 'sum', field='sum') \
            .metric('subtraction', 'sum', field='subtraction') \
            .metric('neutral', 'sum', field='neutral')

        return es_query

    def get_available_days(self):
        return self._get_available_days('date')