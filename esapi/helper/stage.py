from datetime import datetime
from functools import reduce

from elasticsearch_dsl import A
from elasticsearch_dsl.query import Q

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESStageHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stage"
        file_extensions = ['etapas']
        super(ESStageHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('boardingTime', valid_operator_list)

    def get_available_days_between_dates(self, start_date, end_date, valid_operator_list=None):
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        days_in_between = []
        days = self._get_available_days('boardingTime', valid_operator_list)
        for day in days:
            day_obj = datetime.strptime(day, date_format)
            if start_date <= day_obj <= end_date:
                days_in_between.append(day)
        return days_in_between

    def get_transfers_base_query(self, dates, day_types, communes):
        es_query = self.get_base_query()[:0]

        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q('range', boardingTime={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        if day_types:
            es_query = es_query.filter('terms', dayType=day_types)

        if communes:
            es_query = es_query.filter('terms', boardingStopCommune=communes)

        return es_query

    def get_post_products_transfers_data_query(self, dates, day_types, communes):
        es_query = self.get_transfers_base_query(dates, day_types, communes)

        # it uses only rows when stage value is greater than 1
        es_query = es_query.filter('range', stageNumber={'gt': 1})

        aggregation = A('terms', field='dayType', size=4)
        bucket_name = 'result'
        es_query.aggs.bucket(bucket_name, aggregation). \
            bucket('boardingStopCommune', 'terms', field='boardingStopCommune', size=48). \
            bucket('authStopCode', 'terms', field='authStopCode', size=13000). \
            bucket('halfHourInBoardingTime', 'terms', field='halfHourInBoardingTime', size=48). \
            metric('expandedBoarding', 'avg', field='expandedBoarding')

        return es_query

    def get_post_products_aggregated_transfers_data_query(self, dates, day_types, communes):
        es_query = self.get_transfers_base_query(dates, day_types, communes)

        # it uses only rows when stage value is greater than 1
        es_query = es_query.filter('range', stageNumber={'gt': 1})

        bucket_name = 'result'
        es_query.aggs.bucket(bucket_name, 'date_histogram', field='boardingTime', interval='day'). \
            bucket('dayType', 'terms', field='dayType', size=4). \
            bucket('boardingStopCommune', 'terms', field='boardingStopCommune', size=48). \
            bucket('authStopCode', 'terms', field='authStopCode', size=13000). \
            bucket('halfHourInBoardingTime', 'terms', field='halfHourInBoardingTime', size=48). \
            metric('expandedBoarding', 'avg', field='expandedBoarding')

        return es_query

    def get_post_products_aggregated_transfers_data_by_operator_query(self, dates, day_types):
        """
        Get all transfer grouped by day type, period, half hour, auth stop
         code, operator, bus station, transactions number and distribution percentage
        Args:
            dates: date range to get information
            day_types: day type filter

        Returns: transfers query

        """
        es_query = self.get_transfers_base_query(dates, day_types, communes=None)

        bucket_name = 'result'
        es_query.aggs.bucket(bucket_name, 'date_histogram', field='boardingTime', interval='day'). \
            bucket('dayType', 'terms', field='dayType', size=4). \
            bucket('timePeriodInBoardingTime', 'terms', field='timePeriodInBoardingTime', size=100). \
            bucket('authStopCode', 'terms', field='authStopCode', size=12000). \
            bucket('operator', 'terms', field='operator', size=20). \
            bucket('busStation', 'terms', field='busStation', size=2). \
            metric('expandedBoarding', 'sum', field='expandedBoarding')

        return es_query
