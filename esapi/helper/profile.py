# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import A, Q

from localinfo.helper import get_operator_list_for_select_input

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist


class ESProfileHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "profile"
        file_extensions = ['profile']
        super(ESProfileHelper, self).__init__(index_name, file_extensions)

    def get_profile_by_stop_data(self, start_date, end_date, day_type, stop_code, period, half_hour,
                                 valid_operator_list):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist

        if stop_code:
            es_query = es_query.query(Q({'term': {"authStopCode.raw": stop_code}}))
        else:
            raise ESQueryStopParameterDoesNotExist()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStopTime=period)
        if half_hour:
            es_query = es_query.filter('terms', halfHourInStopTime=half_hour)

        es_query = es_query.filter("range", expeditionStartTime={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        es_query = es_query.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'expeditionDayId',
                                    'userStopName', 'expandedAlighting', 'expandedBoarding', 'fulfillment',
                                    'stopDistanceFromPathStart', 'expeditionStartTime',
                                    'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                    'dayType', 'timePeriodInStopTime', 'loadProfile', 'busStation', 'path'])

        return es_query

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('expeditionStartTime', valid_operator_list)

    def get_available_routes(self, valid_operator_list):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

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

    def get_base_profile_by_expedition_data_query(self, start_date, end_date, day_type, auth_route, period, half_hour,
                                                  valid_operator_list):
        es_query = self.get_base_query()

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
            half_hour = map(lambda x: int(x), half_hour)
            es_query = es_query.filter('terms', halfHourInStartTime=half_hour)

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter("range", expeditionStartTime={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        es_query = es_query.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'loadProfile',
                                    'expeditionDayId', 'expandedAlighting', 'expandedBoarding',
                                    'stopDistanceFromPathStart', 'expeditionStartTime', 'expeditionEndTime',
                                    'authStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                                    'fulfillment', 'busStation', 'path'])
        return es_query

    def get_profile_by_expedition_data(self, start_date, end_date, day_type, auth_route, period, half_hour,
                                       valid_operator_list):
        es_query = self.get_base_profile_by_expedition_data_query(start_date, end_date, day_type, auth_route, period,
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
            metric('pathDistance', 'top_hits', size=1, _source=['stopDistanceFromPathStart'])

        # bus station list
        es_query.aggs.bucket('stop', A('filter', Q('term', busStation=1))). \
            bucket('station', A('terms', field='authStopCode.raw', size=500))

        return es_query
