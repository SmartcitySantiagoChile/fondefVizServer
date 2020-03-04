# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

import mock
from elasticsearch_dsl import Search

from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.errors import ESQueryOperatorParameterDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty


class ESODByRouteIndexTest(TestCase):

    def setUp(self):
        self.instance = ESODByRouteHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days(valid_operator_list=[])
        self.assertListEqual(result, [])

    def test_get_available_routes_without_operator_list(self):
        self.assertRaises(ESQueryOperatorParameterDoesNotExist,
                          self.instance.get_available_routes, valid_operator_list=[])

    @mock.patch('localinfo.helper.get_operator_list_for_select_input')
    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_base_query')
    def test_get_available_routes(self, get_base_query, get_operator_list_for_select_input):
        mock_hit = mock.Mock()
        mock_hit.to_dict.return_value = {
            'key': '506 00I',
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'operator': '1',
                        'userRouteCode': '506'
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
        type(get_base_query).buckets = mock.PropertyMock(return_value=[mock_hit])
        get_operator_list_for_select_input.return_value = []
        result, operator_list = self.instance.get_available_routes(valid_operator_list=[1, 2, 3])
        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [])

    def test_get_base_query_for_od(self):
        auth_route_code = ''
        time_periods = [1, 2]
        day_type = ['LABORAL']
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_query_for_od, auth_route_code,
                          time_periods, day_type, start_date, end_date, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_base_query_for_od, auth_route_code,
                          time_periods, day_type, start_date, end_date, valid_operator_list)
        auth_route_code = 'route'
        result = self.instance.get_base_query_for_od(auth_route_code, time_periods, day_type, start_date, end_date,
                                                     valid_operator_list)
        expected = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'authRouteCode': u'route'}},
                       {'terms': {'timePeriodInStopTime': [1, 2]}}, {'terms': {'dayType': [u'LABORAL']}}, {'range': {
                    'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                             u'format': u'yyyy-MM-dd'}}}]}}}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_base_query_for_od')
    def test_get_od_data(self, get_base_query_for_od):
        es_query = mock.MagicMock()
        es_query.execute.return_value = es_query
        es_query.__getitem__.return_value = es_query
        es_query.source.return_value = es_query
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).start = mock.PropertyMock(return_value=es_query)
        hit = mock.Mock()
        hit.to_dict.return_value = {
            'key': '506 00I',
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'userStartStopCode': 1,
                        'startStopName': 2,
                        'startStopOrder': 3
                    }}]
                }
            },
            'end': {
                'buckets': [{'key': '506 00I',
                             'expandedTripNumber': {
                                 'value': 0
                             },
                             'additionalInfo': {
                                 'hits': {
                                     'hits': [{'_source': {
                                         'userEndStopCode': 1,
                                         'endStopName': 2,
                                         'endStopOrder': 3
                                     }}]
                                 }
                             }}]
            }
        }
        type(es_query).buckets = mock.PropertyMock(return_value=[hit])
        get_base_query_for_od.return_value = es_query
        result = [{
            'origin': {
                'authStopCode': '506 00I',
                'userStopCode': 1,
                'userStopName': 2,
                'order': 3
            },
            'destination': [{
                'authStopCode': '506 00I',
                'userStopCode': 1,
                'userStopName': 2,
                'order': 3,
                'value': 0
            }],
        }]
        auth_route_code = ''
        time_periods = []
        day_type = ['LABORAL']
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        valid_operator_list = [1, 2, 3]
        matrix, max_value = self.instance.get_od_data(auth_route_code, time_periods, day_type, start_date, end_date,
                                                      valid_operator_list)
        self.assertListEqual(matrix, result)
        self.assertEqual(max_value, 0)

    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_base_query_for_od')
    def test_get_od_data_without_result(self, get_base_query_for_od):
        es_query = mock.MagicMock()
        es_query.execute.return_value = es_query
        es_query.__getitem__.return_value = es_query
        es_query.source.return_value = es_query
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).start = mock.PropertyMock(return_value=es_query)
        type(es_query).buckets = mock.PropertyMock(return_value=[])
        get_base_query_for_od.return_value = es_query
        auth_route_code = ''
        time_periods = []
        day_type = ['LABORAL']
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryResultEmpty, self.instance.get_od_data, auth_route_code, time_periods, day_type,
                          start_date, end_date, valid_operator_list)
