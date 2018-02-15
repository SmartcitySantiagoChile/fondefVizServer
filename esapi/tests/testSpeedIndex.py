# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from mock import mock

from elasticsearch_dsl import Search

from esapi.helper.speed import ESSpeedHelper
from esapi.tests.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryResultEmpty, ESQueryStopParameterDoesNotExist, ESQueryStopPatternTooShort

from localinfo.models import Operator

import json


class ESSpeedIndexTest(TestCase):

    def setUp(self):
        self.instance = ESSpeedHelper()

    def test_ask_for_base_params(self):
        result = self.instance.get_base_params()

        self.assertIn('day_types', result.keys())

        for key in result:
            self.assertIsInstance(result[key], Search)

    @mock.patch('esapi.helper.profile.ElasticSearchHelper.make_multisearch_query_for_aggs')
    def test_get_route_list(self, mock_method):
        mock_method.return_value = {'routes': []}

        result = self.instance.get_route_list()
        self.assertListEqual(result, [])

    @mock.patch('esapi.helper.profile.ElasticSearchHelper.make_multisearch_query_for_aggs')
    def test_ask_for_available_days(self, mock_method):
        mock_method.return_value = {'days': []}

        result = self.instance.ask_for_available_days()
        self.assertListEqual(result, [])

    @mock.patch('esapi.helper.profile.Search.execute')
    def test_ask_for_available_routes(self, mock_method):
        mock_bucket = mock.Mock()
        type(mock_bucket).aggregations = mock.PropertyMock(return_value=mock_bucket)
        type(mock_bucket).route = mock.PropertyMock(return_value=mock_bucket)
        mock_hit = mock.Mock()
        mock_hit.to_dict.return_value = {
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
        type(mock_bucket).buckets = mock.PropertyMock(return_value=[mock_hit])
        mock_method.return_value = mock_bucket

        # create operator
        Operator.objects.create(esId=1, name='Metbus', description='description')

        result, operator_list = self.instance.ask_for_available_routes()

        self.assertDictEqual(result, {1: {'506I': ['506 00I']}})
        self.assertListEqual(operator_list, [{'id': 1, 'text': 'Metbus'}])

    def test_ask_for_speed_data_with_error(self):
        start_date = ''
        end_date = ''
        day_type = ['LABORAL']
        auth_route = ''

        self.assertRaises(ESQueryRouteParameterDoesNotExist,
                          self.instance.ask_for_speed_data, auth_route, day_type, start_date, end_date)
        auth_route = 'PA433'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist,
                          self.instance.ask_for_speed_data, auth_route, day_type, start_date, end_date)
        start_date = '2018-01-01'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist,
                          self.instance.ask_for_speed_data, auth_route, day_type, start_date, end_date)

    @mock.patch('esapi.helper.speed.Search.execute')
    def test_ask_for_speed_data(self, mock_method):
        mock_bucket = mock.Mock()
        mock_period = mock.Mock()
        mock_section = mock.Mock()

        type(mock_bucket).aggregations = mock.PropertyMock(return_value=mock_bucket)
        type(mock_bucket).periods = mock.PropertyMock(return_value=mock_bucket)

        type(mock_period).key = mock.PropertyMock(return_value='key')
        type(mock_period).sections = mock.PropertyMock(return_value=mock_period)

        type(mock_section).key = mock.PropertyMock(return_value='key2')
        type(mock_section).time = mock.PropertyMock(return_value=mock_section)
        type(mock_section).value = mock.PropertyMock(return_value=0)
        type(mock_section).n_obs = mock.PropertyMock(return_value=mock_section)

        type(mock_period).buckets = mock.PropertyMock(return_value=[mock_section])
        type(mock_bucket).buckets = mock.PropertyMock(return_value=[mock_period])
        mock_method.return_value = mock_bucket

        start_date = '2018-01-01'
        end_date = '2018-02-01'
        day_type = ['LABORAL']
        auth_route = '506 00I'

        result = self.instance.ask_for_speed_data(auth_route, day_type, start_date, end_date)

        self.assertDictEqual(result, {('key2', 'key'): (-1, 0)})

    def test_ask_for_ranking_data(self):
        pass

    def test_for_detail_ranking_data(self):
        pass

    def test_ask_for_speed_variation(self):
        pass


class MatrixData(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:matrixData')
        self.data = {
            'startDate': '',
            'endDate': '',
            'authRoute': '',
            'dayType[]': [],
        }

    def test_wrong_route(self):
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_wrong_start_date(self):
        self.data['endDate'] = '2018-01-01'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())

    def test_wrong_end_date(self):
        self.data['startDate'] = '2018-01-01'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_with_result(self, es_query):
        es_query.return_value = es_query
        es_query.filter.return_value = es_query
        es_query.source.return_value = es_query
        # for shape helper
        es_query.execute.return_value = es_query
        type(es_query).hits = mock.PropertyMock(return_value=es_query)
        type(es_query).total = mock.PropertyMock(return_value=0)

        # for speed data
        period_mock = mock.Mock()
        section_mock = mock.Mock()
        type(period_mock).sections = mock.PropertyMock(return_value=period_mock)
        type(period_mock).buckets = mock.PropertyMock(return_value=[section_mock])
        type(section_mock).key = mock.PropertyMock(return_value='key')
        type(section_mock).time = mock.PropertyMock(return_value=section_mock)
        type(section_mock).value = mock.PropertyMock(return_value=0)

        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).periods = mock.PropertyMock(return_value=es_query)
        type(es_query).buckets = mock.PropertyMock(return_value=[period_mock])
        # for scan
        item = mock.Mock()
        item.to_dict.return_value = {

        }
        es_query.scan.return_value = [item]

        data = {
            'startDate': '2018-01-01',
            'endDate': '2018-01-01',
            'authRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        response = self.client.get(self.url, data)
        print(response.content)
        self.assertNotContains(response, 'status')
        es_query.scan.assert_called_once()

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, es_query):
        es_query.return_value = es_query
        es_query.filter.return_value = es_query
        es_query.source.return_value = es_query
        es_query.scan.return_value = []

        self.data['startDate'] = '2018-01-01'
        self.data['endDate'] = '2018-01-01'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)

        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        es_query.scan.assert_called_once()


class LoadProfileByStop(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:loadProfileByStopData')
        self.data = {
            'startDate': '',
            'endDate': '',
            'stopCode': '',
            'dayType[]': [],
            'period': [],
            'halfHour': []
        }

    def test_wrong_stop_code(self):
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryStopParameterDoesNotExist().get_status_response())

    def test_wrong_start_date(self):
        self.data['endDate'] = '2018-01-01'
        self.data['stopCode'] = 'PA433'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())

    def test_wrong_end_date(self):
        self.data['startDate'] = '2018-01-01'
        self.data['stopCode'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_with_result(self, es_query):
        es_query.return_value = es_query
        es_query.filter.return_value = es_query
        es_query.query.return_value = es_query
        es_query.source.return_value = es_query
        item = mock.Mock()
        item.to_dict.return_value = {
            'expeditionStartTime': '2017-07-31T16:59:11.000Z',
            'expeditionStopTime': '2017-07-31T17:39:36.000Z',
            'expeditionEndTime': '2017-07-31T18:39:41.000Z',
            'dayType': 'LABORAL',
            'stopDistanceFromPathStart': 9663,
            'timePeriodInStartTime': '08 - FUERA DE PUNTA TARDE',
            'timePeriodInStopTime': '09 - PUNTA TARDE',
            'expeditionDayId': 152,
            'expeditionStopOrder': 25,
            'licensePlate': 'ZN-6496',
            'route': 'T101 00I',
            'busCapacity': 91,
            'fulfillment': 'C',
            'userStopName': 'Lo Espinoza esq- / Carmen Lidia',
            'userStopCode': 'PJ2',
            'authStopCode': 'T-8-65-NS-10',
            'busStation': '0',
            'expandedBoarding': 1.215768337,
            'loadProfile': 36.33063507,
            'expandedAlighting': 1.073773265
        }
        es_query.scan.return_value = [item]

        data = {
            'startDate': '2018-01-01',
            'endDate': '2018-01-01',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'stopCode': 'PA433'
        }
        response = self.client.get(self.url, data)

        self.assertNotContains(response, 'status')
        es_query.scan.assert_called_once()

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, es_query):
        es_query.return_value = es_query
        es_query.filter.return_value = es_query
        es_query.query.return_value = es_query
        es_query.source.return_value = es_query
        es_query.scan.return_value = []

        self.data['startDate'] = '2018-01-01'
        self.data['endDate'] = '2018-01-01'
        self.data['stopCode'] = '506 00I'
        response = self.client.get(self.url, self.data)

        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        es_query.scan.assert_called_once()


class AskForStops(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:matchedStopData')
        self.data = {
            'term': ''
        }

        self.item = mock.Mock()
        type(self.item).aggregations = mock.PropertyMock(return_value=self.item)
        type(self.item).unique = mock.PropertyMock(return_value=self.item)
        type(self.item).buckets = mock.PropertyMock(return_value=[self.item])

    def test_empty_stop_pattern(self):
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryStopPatternTooShort().get_status_response())

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result(self, es_multi_query):
        es_multi_query.return_value = es_multi_query
        es_multi_query.add.return_value = es_multi_query
        type(self.item).doc_count = 0
        es_multi_query.execute.return_value = [self.item]

        self.data['term'] = 'PA4'
        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        es_multi_query.execute.assert_called_once()

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result_with_key_as_string(self, es_multi_query):
        es_multi_query.return_value = es_multi_query
        es_multi_query.add.return_value = es_multi_query

        type(self.item).doc_count = mock.PropertyMock(return_value=1)
        self.item.__iter__ = mock.Mock(return_value=iter(['key_as_string']))
        type(self.item).key_as_string = mock.PropertyMock(return_value='PA433')
        es_multi_query.execute.return_value = [self.item]

        self.data['term'] = 'PA4'
        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        answer = {
            'items': [{
                'id': 'PA433',
                'text': 'PA433'
            }]
        }
        self.assertJSONEqual(response.content, answer)
        es_multi_query.execute.assert_called_once()

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result_without_key_as_string(self, es_multi_query):
        es_multi_query.return_value = es_multi_query
        es_multi_query.add.return_value = es_multi_query
        type(self.item).doc_count = mock.PropertyMock(return_value=1)
        self.item.__iter__ = mock.Mock(return_value=iter([]))
        type(self.item).key = mock.PropertyMock(return_value='PA433')
        es_multi_query.execute.return_value = [self.item]

        self.data['term'] = 'PA4'
        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        answer = {
            'items': [{
                'id': 'PA433',
                'text': 'PA433'
            }]
        }
        self.assertJSONEqual(response.content, answer)
        es_multi_query.execute.assert_called_once()


class AskForAvailableDays(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:availableSpeedDays')
        self.data = {}
        self.available_date = '2018-01-01'

        self.item = mock.Mock()
        type(self.item).aggregations = mock.PropertyMock(return_value=self.item)
        type(self.item).unique = mock.PropertyMock(return_value=self.item)
        type(self.item).buckets = mock.PropertyMock(return_value=[self.item])
        type(self.item).doc_count = mock.PropertyMock(return_value=1)
        self.item.__iter__ = mock.Mock(return_value=iter([]))
        type(self.item).key = mock.PropertyMock(return_value=self.available_date)

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_ask_for_days_with_data(self, es_multi_query):
        es_multi_query.return_value = es_multi_query
        es_multi_query.add.return_value = es_multi_query
        type(self.item).doc_count = 1
        es_multi_query.execute.return_value = [self.item]

        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        answer = {
            'availableDays': [self.available_date]
        }
        self.assertJSONEqual(response.content, answer)
        es_multi_query.execute.assert_called_once()


class AskForAvailableRoutes(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:availableSpeedRoutes')
        self.data = {}
        self.available_route = '506 00I'

        self.item = mock.Mock()
        type(self.item).aggregations = mock.PropertyMock(return_value=self.item)
        type(self.item).route = mock.PropertyMock(return_value=self.item)
        type(self.item).buckets = mock.PropertyMock(return_value=[self.item])
        self.item.to_dict.return_value = {
            'key': self.available_route,
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'operator': '1',
                        'userRoute': '506I'
                    }}]
                }
            }
        }

    @mock.patch('esapi.helper.basehelper.Search')
    def test_ask_for_days_with_data(self, es_query):
        es_query.return_value = es_query
        es_query.__getitem__.return_value = es_query
        es_query.source.return_value = es_query
        type(es_query).aggs = mock.PropertyMock()
        es_query.execute.return_value = self.item

        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        answer = {
            'availableRoutes': {
                '1': {
                    '506I': [self.available_route]
                }
            },
            'operatorDict': []
        }
        self.assertJSONEqual(response.content, answer)
        es_query.execute.assert_called_once()


class TestESSpeedHelper(TestCase):

    def setUp(self):
        self.instance = ESSpeedHelper()

    def test_ask_for_base_params(self):
        result = self.instance.get_base_params()

        self.assertIn('day_types', result.keys())

        for key in result:
            self.assertIsInstance(result[key], Search)

    @mock.patch('esapi.helper.basehelper.Search')
    def test_ask_for_route_list(self, es_query):
        result = self.instance.get_route_list()
        print(result)
        self.assertIsInstance(result, list)
