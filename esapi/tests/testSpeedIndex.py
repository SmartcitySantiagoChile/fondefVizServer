# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.test import TestCase
from elasticsearch_dsl import Search

from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist, ESQueryResultEmpty, \
    ESQueryDateRangeParametersDoesNotExist
from esapi.helper.speed import ESSpeedHelper


class ESSpeedIndexTest(TestCase):

    def setUp(self):
        self.instance = ESSpeedHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days(valid_operator_list=[])
        self.assertListEqual(result, [])

    def test_get_available_routes_without_operator_list(self):
        self.assertRaises(ESQueryOperatorParameterDoesNotExist,
                          self.instance.get_available_routes, valid_operator_list=[])

    @mock.patch('esapi.helper.speed.get_operator_list_for_select_input')
    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_query')
    def test_get_available_routes(self, get_base_query, get_operator_list_for_select_input):
        hit = mock.Mock()
        hit.to_dict.return_value = {
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
        type(get_base_query).buckets = mock.PropertyMock(return_value=[hit])
        get_operator_list_for_select_input.return_value = list()
        result, operator_list = self.instance.get_available_routes(valid_operator_list=[1, 2, 3])
        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [])

    def test_get_base_speed_data_query(self):
        dates = [[]]
        day_type = ['LABORAL']
        auth_route = ''
        valid_operator_list = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_speed_data_query, auth_route,
                          day_type, dates, valid_operator_list)
        dates = [["2018-01-01", "2018-01-02"]]
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_speed_data_query, auth_route,
                          day_type, dates, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_base_speed_data_query, auth_route,
                          day_type, dates, valid_operator_list)
        auth_route = '506 00I'
        result = self.instance.get_base_speed_data_query(auth_route, day_type, dates,
                                                         valid_operator_list)
        expected = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'authRouteCode': u'506 00I'}},
                       {'terms': {'dayType': [u'LABORAL']}},
                       {'range': {'date': {u'gte': u'2018-01-01', u'lte': u'2018-01-02', u'format': u'yyyy-MM-dd'}}}]}}}
        print (result.to_dict())

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_speed_data_query')
    def test_get_speed_data(self, get_base_speed_data_query):
        es_query = mock.MagicMock()
        period = mock.Mock()
        section = mock.Mock()

        es_query.execute.return_value = es_query

        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).periods = mock.PropertyMock(return_value=es_query)

        type(period).key = mock.PropertyMock(return_value='key')
        type(period).sections = mock.PropertyMock(return_value=period)

        type(section).key = mock.PropertyMock(return_value='key2')
        type(section).time = mock.PropertyMock(return_value=section)
        type(section).value = mock.PropertyMock(return_value=0)
        type(section).n_obs = mock.PropertyMock(return_value=section)

        type(period).buckets = mock.PropertyMock(return_value=[section])
        type(es_query).buckets = mock.PropertyMock(return_value=[period])

        es_query.__getitem__.return_value = es_query
        get_base_speed_data_query.return_value = es_query

        dates = "[['2018-01-01']]"
        day_type = ['LABORAL']
        auth_route = '506 00I'
        valid_operator_list = [1, 2, 3]
        result = self.instance.get_speed_data(auth_route, day_type, dates, valid_operator_list)
        self.assertDictEqual(result, {('key2', 'key'): (-1, 0, list(result.values())[0][2], 0)})

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_speed_data_query')
    def test_get_speed_data_without_result(self, get_base_speed_data_query):
        es_query = mock.MagicMock()
        es_query.execute.return_value = es_query
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).periods = mock.PropertyMock(return_value=es_query)
        type(es_query).buckets = mock.PropertyMock(return_value=[])
        es_query.__getitem__.return_value = es_query
        get_base_speed_data_query.return_value = es_query
        dates = [['2018-01-01', '2018-02-01']]
        day_type = ['LABORAL']
        auth_route = '506 00I'
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryResultEmpty, self.instance.get_speed_data, auth_route, day_type, dates,
                          valid_operator_list)

    def test_get_base_ranking_data_query(self):
        dates = []
        hour_period_from = ''
        hour_period_to = ''
        day_type = ['LABORAL']
        valid_operator_list = []
        route_list = [1, 2, 3]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_ranking_data_query, dates,
                          hour_period_from, hour_period_to, day_type, valid_operator_list)
        dates = [['2018-01-01']]
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_ranking_data_query, dates,
                          hour_period_from, hour_period_to, day_type, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        result = self.instance.get_base_ranking_data_query(dates, hour_period_from, hour_period_to,
                                                           day_type, valid_operator_list, route_list)
        expected = {'query': {'bool': {'filter': [{'terms': {'operator': [1, 2, 3]}}, {
            'range': {'date': {u'gte': u'2018-01-01', u'lte': u'2018-01-01', u'format': u'yyyy-MM-dd'}}},
                                                  {'range': {'periodId': {u'gte': u'', u'lte': u''}}},
                                                  {'bool': {'must_not': [{'term': {'section': 0}}]}},
                                                  {'bool': {'must_not': [{'term': {'isEndSection': 1}}]}},
                                                  {'terms': {'authRouteCode': [1, 2, 3]}},
                                                  {'terms': {'dayType': [u'LABORAL']}}]}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_ranking_data_query')
    def test_get_ranking_data(self, get_base_ranking_data_query):
        dates = "[['2018-01-01']]"
        hour_period_from = ''
        hour_period_to = ''
        day_type = ['LABORAL']
        valid_operator_list = []
        self.assertRaises(ESQueryResultEmpty, self.instance.get_ranking_data, dates,
                          hour_period_from, hour_period_to, day_type, valid_operator_list)

        es_query = mock.Mock()
        tup = mock.Mock()

        es_query.execute.return_value = es_query
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).tuples = mock.PropertyMock(return_value=es_query)

        type(tup).key = mock.PropertyMock(return_value='1-2-3')
        type(tup).time = mock.PropertyMock(return_value=tup)
        type(tup).distance = mock.PropertyMock(return_value=tup)
        type(tup).speed = mock.PropertyMock(return_value=tup)

        type(tup).value = mock.PropertyMock(return_value=5)
        type(tup).n_obs = mock.PropertyMock(return_value=tup)

        type(es_query).buckets = mock.PropertyMock(return_value=[tup])
        get_base_ranking_data_query.return_value = get_base_ranking_data_query
        get_base_ranking_data_query.__getitem__.return_value = es_query

        result = self.instance.get_ranking_data(dates, hour_period_from, hour_period_to, day_type,
                                                valid_operator_list)
        expected = [{
            u'n_obs': 5,
            u'distance': 5,
            u'route': u'1',
            u'period': 3,
            u'time': 5,
            u'speed': 5,
            u'section': 2
        }]
        self.assertListEqual(result, expected)

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_ranking_data_query')
    def test_get_ranking_data_without_result(self, get_base_ranking_data_query):
        dates = "[['2018-01-01', '2018-02-01']]"
        hour_period_from = ''
        hour_period_to = ''
        day_type = ['LABORAL']
        valid_operator_list = []

        es_query = mock.Mock()
        tup = mock.Mock()

        es_query.execute.return_value = es_query
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).tuples = mock.PropertyMock(return_value=es_query)

        type(tup).key = mock.PropertyMock(return_value='1-2-3')
        type(tup).time = mock.PropertyMock(return_value=tup)
        type(tup).distance = mock.PropertyMock(return_value=tup)
        type(tup).speed = mock.PropertyMock(return_value=tup)

        type(tup).value = mock.PropertyMock(return_value=1)
        type(tup).n_obs = mock.PropertyMock(return_value=tup)

        type(es_query).buckets = mock.PropertyMock(return_value=[tup])
        get_base_ranking_data_query.return_value = get_base_ranking_data_query
        get_base_ranking_data_query.__getitem__.return_value = es_query

        self.assertRaises(ESQueryResultEmpty, self.instance.get_ranking_data, dates, hour_period_from,
                          hour_period_to, day_type, valid_operator_list)

    def test_get_base_detail_ranking_data_query(self):
        route = 'route'
        dates = []
        period = 1
        day_type = ['LABORAL']
        valid_operator_list = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_detail_ranking_data_query, route,
                          dates, period, day_type, valid_operator_list)
        dates = [['2018-01-01', '2018-02-01']]
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_detail_ranking_data_query, route,
                          dates, period, day_type, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        result = self.instance.get_base_detail_ranking_data_query(route, dates, period, day_type,
                                                                  valid_operator_list)
        expected = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'authRouteCode': u'route'}},
                       {'range': {'date': {u'gte': u'2018-01-01', u'lte': u'2018-02-01', u'format': u'yyyy-MM-dd'}}},
                       {'term': {'periodId': 1}}, {'terms': {'dayType': [u'LABORAL']}}]}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_detail_ranking_data(self):
        result = self.instance.get_detail_ranking_data('route', [['2018-01-01', '2018-02-01']],
                                                       1, ['LABORAL'], [1, 2, 3])
        expected = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3]}}, {'term': {'authRouteCode': u'route'}},
                       {'range': {'date': {u'gte': u'2018-01-01', u'lte': u'2018-02-01', u'format': u'yyyy-MM-dd'}}},
                       {'term': {'periodId': 1}}, {'terms': {'dayType': [u'LABORAL']}}]}}, 'from': 0, 'aggs': {
            u'sections': {'terms': {'field': u'section', 'size': 200}, 'aggs': {u'n_obs': {'sum': {'field': u'nObs'}},
                                                                                u'distance': {
                                                                                    'sum': {'field': u'totalDistance'}},
                                                                                u'speed': {'bucket_script': {
                                                                                    'buckets_path': {u'd': u'distance',
                                                                                                     u't': u'time'},
                                                                                    'script': u'params.d / params.t'}},
                                                                                u'time': {
                                                                                    'sum': {'field': u'totalTime'}}}}},
            'size': 0}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_variation_speed_query(self):
        dates = [['2018-01-01', '2018-02-01']]
        day_type = ['LABORAL']
        user_route = 'route'
        operator = 'operator'
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_variation_speed_query,
                          dates[0][0], dates[0][-1], day_type, user_route, operator, valid_operator_list)
        valid_operator_list = ['operator']
        result = self.instance.get_base_variation_speed_query(dates[0][0], dates[0][-1], day_type, user_route, operator,
                                                              valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'range': {
            'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                     u'format': u'yyyy-MM-dd'}}}, {'term': {'operator': u'operator'}},
            {'term': {'userRouteCode': u'route'}},
            {'terms': {'dayType': [u'LABORAL']}}]}}}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_speed_variation_data(self):
        result = self.instance.get_speed_variation_data('2018-01-01', '2018-02-01', ['LABORAL'], 'route', 1,
                                                        [1, 2, 3])
        expected = {'query': {'bool': {'filter': [{'range': {
            'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                     u'format': u'yyyy-MM-dd'}}}, {'term': {'operator': 1}}, {'term': {'userRouteCode': u'route'}},
            {'terms': {'dayType': [u'LABORAL']}}]}}, 'from': 0, 'aggs': {
            u'routes': {'terms': {'field': u'authRouteCode', 'size': 2000}, 'aggs': {
                u'periods': {'terms': {'field': u'periodId', 'size': 50}, 'aggs': {u'days': {
                    'range': {'ranges': [{u'to': u'2018-02-01'}, {u'from': u'2018-02-01'}], 'field': u'date',
                              'format': u'yyyy-MM-dd'},
                    'aggs': {u'n_obs': {'sum': {'field': u'nObs'}}, u'distance': {'sum': {'field': u'totalDistance'}},
                             u'stats': {'extended_stats': {'field': u'speed'}}, u'speed': {
                            'bucket_script': {'buckets_path': {u'd': u'distance', u't': u'time'},
                                              'script': u'params.d / params.t * 3.6'}},
                             u'time': {'sum': {'field': u'totalTime'}}}}}}}}}, 'size': 0}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)
