from functools import reduce

from elasticsearch_dsl import A
from elasticsearch_dsl import Q

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESPaymentFactorHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "paymentfactor"
        file_extensions = ['paymentfactor']
        super(ESPaymentFactorHelper, self).__init__(index_name, file_extensions)

    def get_data(self, dates, day_type):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()

        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q('range', date={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
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
