# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

import mock

from esapi.helper.profile import ESProfileHelper
from elasticsearch_dsl import Search
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryOperatorParameterDoesNotExist, ESQueryStopParameterDoesNotExist


class ESProfileIndexTest(TestCase):

    def setUp(self):
        self.instance = ESProfileHelper()

    def test_get_profile_by_stop_data(self):
        dates = [[""]]
        day_type = ['LABORAL']
        stop_code = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_profile_by_stop_data, dates,
                          day_type, stop_code, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_profile_by_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        stop_code = 'PA433'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_profile_by_stop_data(dates, day_type, stop_code, period, half_hour,
                                                        valid_operator_list)
        expected = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3]}}, {'terms': {'dayType': [u'LABORAL']}},
                       {'terms': {'timePeriodInStopTime': [1, 2, 3]}}, {'terms': {'halfHourInStopTime': [1, 2, 3]}}, {
                           'range': {'expeditionStartTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d',
                                                             u'lte': u'2018-01-02||/d', u'format': u'yyyy-MM-dd'}}}],
            'must': [{'term': {u'authStopCode.raw': u'PA433'}}]}},
            '_source': [u'busCapacity', u'expeditionStopTime', u'licensePlate', u'route', u'expeditionDayId',
                        u'userStopName', u'expandedAlighting', u'expandedBoarding', u'fulfillment',
                        u'stopDistanceFromPathStart', u'expeditionStartTime', u'expeditionEndTime',
                        u'authStopCode', u'userStopCode', u'timePeriodInStartTime', u'dayType',
                        u'timePeriodInStopTime', u'loadProfile', u'busStation', u'path']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days(valid_operator_list=[])
        self.assertListEqual(result, [])

    def test_get_available_routes_without_operator_list(self):
        self.assertRaises(ESQueryOperatorParameterDoesNotExist,
                          self.instance.get_available_routes, valid_operator_list=[])

    @mock.patch('esapi.helper.profile.get_operator_list_for_select_input')
    @mock.patch('esapi.helper.profile.ESProfileHelper.get_base_query')
    def test_get_available_routes(self, get_base_query, get_operator_list_for_select_input):
        hit = mock.Mock()
        hit.to_dict.return_value = {
            'key': '506 00I',
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'operator': '1',
                        'userRoute': '506'
                    }}]
                }
            }
        }
        get_base_query.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.source.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).route = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[hit])
        get_operator_list_for_select_input.return_value = [1, 2]
        result, operator_list = self.instance.get_available_routes(valid_operator_list=[1, 2, 3])
        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [1, 2])

    def test_get_base_profile_by_expedition_data_query(self):
        dates = [[""]]
        day_type = ['LABORAL']
        auth_route = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_profile_by_expedition_data,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_profile_by_expedition_data, dates,
                          day_type, auth_route, period, half_hour, valid_operator_list)
        auth_route = '506 00I'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_expedition_data,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_base_profile_by_expedition_data_query(dates, day_type, auth_route,
                                                                         period, half_hour,
                                                                         valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'route': u'506 00I'}},
                                                  {'terms': {'dayType': [u'LABORAL']}},
                                                  {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-02||/d',
                                        u'format': u'yyyy-MM-dd'}}}, {'term': {'notValid': 0}}]}},
                    '_source': [u'busCapacity', u'licensePlate', u'route', u'loadProfile', u'expeditionDayId',
                                u'expandedAlighting', u'expandedBoarding', u'expeditionStartTime', u'expeditionEndTime',
                                u'authStopCode', u'timePeriodInStartTime', u'dayType', u'timePeriodInStopTime',
                                u'busStation', u'path', u'notValid']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_profile_by_expedition_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        result = self.instance.get_profile_by_expedition_data(dates, ['LABORAL'], 'route', [1, 2, 3],
                                                              [1, 2, 3], [1, 2, 3])
        expected = {'query': {'bool': {'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'route': u'route'}},
                                                  {'terms': {'dayType': [u'LABORAL']}},
                                                  {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                                        u'format': u'yyyy-MM-dd'}}}, {'term': {'notValid': 0}}]}},
                    '_source': [u'busCapacity', u'licensePlate', u'route', u'loadProfile', u'expeditionDayId',
                                u'expandedAlighting', u'expandedBoarding', u'expeditionStartTime', u'expeditionEndTime',
                                u'authStopCode', u'timePeriodInStartTime', u'dayType', u'timePeriodInStopTime',
                                u'busStation', u'path', u'notValid'], 'from': 0, 'aggs': {
                u'stop': {'filter': {'term': {'busStation': 1}},
                          'aggs': {u'station': {'terms': {'field': u'authStopCode.raw', 'size': 500}}}},
                u'stops': {'terms': {'field': u'authStopCode.raw', 'size': 500},
                           'aggs': {u'expandedBoarding': {'avg': {'field': u'expandedBoarding'}},
                                    u'expandedAlighting': {'avg': {'field': u'expandedAlighting'}},
                                    u'loadProfile': {'avg': {'field': u'loadProfile'}},
                                    u'sumBusCapacity': {'sum': {'field': u'busCapacity'}},
                                    u'maxLoadProfile': {'max': {'field': u'loadProfile'}},
                                    u'sumLoadProfile': {'sum': {'field': u'loadProfile'}}, u'busSaturation': {
                                   'bucket_script': {'buckets_path': {u'd': u'sumLoadProfile', u't': u'sumBusCapacity'},
                                                     'script': u'params.d / params.t'}}, u'pathDistance': {
                                   'top_hits': {'size': 1, '_source': [u'stopDistanceFromPathStart']}}}}}, 'size': 0}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_profile_by_trajectory_data_query(self):
        dates = [[""]]
        day_type = ['LABORAL']
        auth_route = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        auth_route = '506 00I'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist,
                          self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_base_profile_by_trajectory_data_query(dates, day_type, auth_route,
                                                                         period, half_hour,
                                                                         valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'route': u'506 00I'}},
                                                  {'terms': {'dayType': [u'LABORAL']}},
                                                  {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-02||/d',
                                        u'format': u'yyyy-MM-dd'}}}]}},
                    '_source': [u'busCapacity', u'licensePlate', u'route', u'loadProfile', u'expeditionDayId',
                                u'expandedAlighting', u'expandedBoarding', u'expeditionStartTime', u'expeditionEndTime',
                                u'authStopCode', u'timePeriodInStartTime', u'dayType', u'timePeriodInStopTime',
                                u'busStation', u'path', u'stopDistanceFromPathStart', u'expeditionStopTime']}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days_between_dates(self, _get_available_days):
        start_date = '2018-01-01'
        end_date = '2018-01-05'
        _get_available_days.return_value = [
            '2018-01-03',
            '2018-02-05',
        ]
        result = self.instance.get_available_days_between_dates(start_date, end_date)
        self.assertIsInstance(result, list)
        self.assertListEqual(result, ['2018-01-03'])
