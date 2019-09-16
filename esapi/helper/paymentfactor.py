# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import A

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESPaymentFactorHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "paymentfactor"
        file_extensions = ['paymentfactor']
        super(ESPaymentFactorHelper, self).__init__(index_name, file_extensions)

    def get_data(self, start_date, end_date, day_type, exclude_dates):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        if exclude_dates:
            print(exclude_dates)
            es_query = es_query.exclude('terms', date=exclude_dates)

        es_query = es_query.filter("range", date={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        # omit hits
        es_query = es_query[:0]

        es_query.aggs \
            .bucket('by_bus_station_id', A('terms', field='busStationId', size=10000)) \
            .bucket('by_bus_station_name', 'terms', field='busStationName') \
            .bucket('by_assignation', 'terms', field='assignation') \
            .bucket('by_operator', 'terms', field='operator') \
            .bucket('by_day_type', 'terms', field='dayType') \
            .metric('total', 'sum', field='total') \
            .metric('sum', 'sum', field='sum') \
            .metric('subtraction', 'sum', field='subtraction') \
            .metric('neutral', 'sum', field='neutral') \
            .bucket('by_date', A('terms', field='date', size=10000)) \
            .metric('factor', 'sum', field='factor')

        return es_query

    def get_available_days(self):
        return self._get_available_days('date')
