# -*- coding: utf-8 -*-


from collections import defaultdict
from datetime import datetime
from functools import reduce

from elasticsearch_dsl import A, Q

from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper
from localinfo.helper import get_operator_list_for_select_input


class ESProfileHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "profile"
        file_extensions = ['profile']
        super(ESProfileHelper, self).__init__(index_name, file_extensions)

    def get_profile_by_stop_data(self, dates, day_type, stop_code, period, half_hour,
                                 valid_operator_list):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()
        es_query = es_query.filter('term', fulfillment="C")
        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist

        if stop_code:
            es_query = es_query.query(Q({'term': {"authStopCode.raw": stop_code}}))
        else:
            raise ESQueryStopParameterDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStopTime=period)
        if half_hour:
            es_query = es_query.filter('terms', halfHourInStopTime=half_hour)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q("range", expeditionStartTime={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        es_query = es_query.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'expeditionDayId',
                                    'userStopName', 'expandedAlighting', 'expandedBoarding', 'fulfillment',
                                    'stopDistanceFromPathStart', 'expeditionStartTime',
                                    'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                    'dayType', 'timePeriodInStopTime', 'loadProfile', 'busStation', 'path',
                                    'expandedEvasionBoarding', 'expandedEvasionAlighting',
                                    'expandedBoardingPlusExpandedEvasionBoarding',
                                    'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
                                    'boardingWithAlighting'])

        return es_query

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('expeditionStartTime', valid_operator_list)

    def get_available_routes(self, valid_operator_list, start_date=None, end_date=None):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])
        es_query = es_query.filter('term', fulfillment="C")
        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()
        if start_date and end_date:
            es_query = es_query.filter('range', expeditionStartTime={
                'gte': '{0} 00:00:00'.format(start_date),
                'format': 'yyyy-MM-dd HH:mm:ss'
            })

            es_query = es_query.filter('range', expeditionStartTime={
                'lte': '{0} 23:59:59'.format(end_date),
                'format': 'yyyy-MM-dd HH:mm:ss'
            })
        aggs = A('terms', field="route", size=5000)
        es_query.aggs.bucket('route', aggs)

        es_query.aggs['route']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['operator', 'userRoute'])

        operator_list = get_operator_list_for_select_input(filter=valid_operator_list)

        result = defaultdict(lambda: defaultdict(list))

        for hit in es_query.execute().aggregations.route.buckets:
            data = hit.to_dict()
            auth_route = data['key']
            operator_id = data['additionalInfo']['hits']['hits'][0]['_source']['operator']
            user_route = data['additionalInfo']['hits']['hits'][0]['_source']['userRoute']

            result[operator_id][user_route].append(auth_route)
        return result, operator_list

    def get_base_profile_by_expedition_data_query(self, dates, day_type, auth_route, period, half_hour,
                                                  valid_operator_list, show_only_valid_expeditions=True):
        es_query = self.get_base_query()
        es_query = es_query.filter('term', fulfillment="C")
        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        if auth_route:
            es_query = es_query.filter('term', route=auth_route)
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStartTime=period)
        if half_hour:
            half_hour = [int(x) for x in half_hour]
            es_query = es_query.filter('terms', halfHourInStartTime=half_hour)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q("range", expeditionStartTime={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)

        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        if show_only_valid_expeditions:
            es_query = es_query.filter('term', notValid=0)

        es_query = es_query.source(
            ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId', 'expandedAlighting',
             'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime', 'authStopCode', 'timePeriodInStartTime',
             'dayType', 'timePeriodInStopTime', 'busStation', 'path', 'notValid', 'expandedEvasionBoarding',
             'expandedEvasionAlighting',
             'expandedBoardingPlusExpandedEvasionBoarding',
             'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
             'boardingWithAlighting'])

        return es_query

    def get_profile_by_expedition_data(self, dates, day_type, auth_route, period, half_hour,
                                       valid_operator_list):
        es_query = self.get_base_profile_by_expedition_data_query(dates, day_type, auth_route, period,
                                                                  half_hour, valid_operator_list)[:0]
        stops = A('terms', field='authStopCode.raw', size=500)
        es_query.aggs.bucket('stops', stops). \
            metric('expandedAlighting', 'avg', field='expandedAlighting'). \
            metric('expandedBoarding', 'avg', field='expandedBoarding'). \
            metric('loadProfile', 'avg', field='loadProfile'). \
            metric('maxLoadProfile', 'max', field='loadProfile'). \
            metric('sumLoadProfile', 'sum', field='loadProfile'). \
            metric('sumBusCapacity', 'sum', field='busCapacity'). \
            metric('busSaturation', 'bucket_script', script='params.d / params.t',
                   buckets_path={'d': 'sumLoadProfile', 't': 'sumBusCapacity'}). \
            metric('pathDistance', 'top_hits', size=1, _source=['stopDistanceFromPathStart']). \
            metric('expandedEvasionBoarding', 'avg', field='expandedEvasionBoarding'). \
            metric('expandedEvasionAlighting','avg', field='expandedEvasionAlighting'). \
            metric('expandedBoardingPlusExpandedEvasionBoarding', 'avg', field='expandedBoardingPlusExpandedEvasionBoarding'). \
            metric('expandedAlightingPlusExpandedEvasionAlighting', 'avg', field='expandedAlightingPlusExpandedEvasionAlighting'). \
            metric('loadProfileWithEvasion', 'avg', field='loadProfileWithEvasion'). \
            metric('boardingWithAlighting', 'sum', field='boardingWithAlighting')

        # bus station list
        es_query.aggs.bucket('stop', A('filter', Q('term', busStation=1))). \
            bucket('station', A('terms', field='authStopCode.raw', size=500))
        return es_query

    def get_base_profile_by_trajectory_data_query(self, dates, day_type, auth_route, period, half_hour,
                                                  valid_operator_list):
        es_query = self.get_base_query()
        es_query = es_query.filter('term', fulfillment="C")
        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        if auth_route:
            es_query = es_query.filter('term', route=auth_route)
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        if period:
            es_query = es_query.filter('terms', timePeriodInStartTime=period)

        if half_hour:
            half_hour = [int(x) for x in half_hour]
            es_query = es_query.filter('terms', halfHourInStartTime=half_hour)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q("range", expeditionStartTime={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
        es_query = es_query.source(
            ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId', 'expandedAlighting',
             'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime', 'authStopCode', 'timePeriodInStartTime',
             'dayType', 'timePeriodInStopTime', 'busStation', 'path', 'stopDistanceFromPathStart',
             'expeditionStopTime', 'notValid', 'expandedEvasionBoarding',
             'expandedEvasionAlighting',
             'expandedBoardingPlusExpandedEvasionBoarding',
             'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
             'boardingWithAlighting'])

        return es_query

    def get_available_days_between_dates(self, start_date, end_date, valid_operator_list=None):
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        days_in_between = []
        days = self._get_available_days('expeditionStartTime', valid_operator_list)
        for day in days:
            day_obj = datetime.strptime(day, date_format)
            if start_date <= day_obj <= end_date:
                days_in_between.append(day)
        return days_in_between

    def get_profile_by_multiple_stop_data(self, dates, day_type, stop_codes, period, half_hour,
                                          valid_operator_list):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()
        es_query = es_query.filter('term', fulfillment="C")
        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist

        if stop_codes:
            es_query = es_query.query(Q({'terms': {"authStopCode.raw": stop_codes}}))
        else:
            raise ESQueryStopParameterDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStopTime=period)
        if half_hour:
            es_query = es_query.filter('terms', halfHourInStopTime=half_hour)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q("range", expeditionStartTime={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
        es_query = es_query[:0]
        aggs = A('terms', field="authStopCode.raw", size=1000)
        es_query.aggs.bucket('stops', aggs). \
            metric('expandedAlighting', 'avg', field='expandedAlighting'). \
            metric('expandedBoarding', 'avg', field='expandedBoarding'). \
            metric('sumExpandedAlighting', 'sum', field='expandedAlighting'). \
            metric('sumExpandedBoarding', 'sum', field='expandedBoarding'). \
            metric('loadProfile', 'avg', field='loadProfile'). \
            metric('maxLoadProfile', 'max', field='loadProfile'). \
            metric('sumLoadProfile', 'sum', field='loadProfile'). \
            metric('sumBusCapacity', 'sum', field='busCapacity'). \
            metric('busSaturation', 'bucket_script', script='params.d / params.t',
                   buckets_path={'d': 'sumLoadProfile', 't': 'sumBusCapacity'}). \
            metric('userStopCode', 'top_hits', size=1, _source=['userStopCode']). \
            metric('userStopName', 'top_hits', size=1, _source=['userStopName']). \
            metric('busCapacity', 'avg', field='busCapacity'). \
            metric('tripsCount', 'value_count', field='expandedAlighting'). \
            metric('expandedEvasionBoarding', 'avg', field='expandedEvasionBoarding'). \
            metric('expandedEvasionAlighting','avg', field='expandedEvasionAlighting'). \
            metric('expandedBoardingPlusExpandedEvasionBoarding', 'avg', field='expandedBoardingPlusExpandedEvasionBoarding'). \
            metric('expandedAlightingPlusExpandedEvasionAlighting', 'avg', field='expandedAlightingPlusExpandedEvasionAlighting'). \
            metric('loadProfileWithEvasion', 'avg', field='loadProfileWithEvasion'). \
            metric('boardingWithAlighting', 'sum', field='boardingWithAlighting')
        return es_query

    def get_all_auth_routes(self, start_date=None, end_date=None):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        if start_date and end_date:
            es_query = es_query.filter('range', expeditionStartTime={
                'gte': '{0} 00:00:00'.format(start_date),
                'format': 'yyyy-MM-dd HH:mm:ss'
            })

            es_query = es_query.filter('range', expeditionEndTime={
                'lte': '{0} 23:59:59'.format(end_date),
                'format': 'yyyy-MM-dd HH:mm:ss'
            })
        aggs = A('terms', field="route", size=5000)
        es_query.aggs.bucket('route', aggs)
        return es_query
