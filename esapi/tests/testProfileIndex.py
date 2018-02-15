# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from mock import mock

from esapi.helper.profile import ESProfileHelper
from elasticsearch_dsl import Search
from esapi.tests.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryResultEmpty, ESQueryStopParameterDoesNotExist, ESQueryStopPatternTooShort

import json


class LoadProfileByExpedition(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()

        self.url = reverse('esapi:loadProfileByExpeditionData')
        self.data = {
            'startDate': '',
            'endDate': '',
            'authRoute': '',
            'dayType[]': [],
            'period[]': [],
            'halfHour[]': []
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
            'authRoute': '506 00I'
        }
        response = self.client.get(self.url, data)

        self.assertNotContains(response, 'status')
        es_query().scan.assert_called_once()

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
        es_query().scan.assert_called_once()


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
        es_query().scan.assert_called_once()

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
        es_query().scan.assert_called_once()


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

        self.url = reverse('esapi:availableProfileDays')
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

        self.url = reverse('esapi:availableProfileRoutes')
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
                        'operator': 'Metbus',
                        'userRoute': '506'
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
                'Metbus': {
                    '506': [self.available_route]
                }
            },
            'operatorDict': []
        }
        self.assertJSONEqual(response.content, answer)
        es_query.execute.assert_called_once()


class AskForBaseParams(TestCase):

    def test_ask_for_base_params(self):
        instance = ESProfileHelper()
        result = instance.get_base_params()

        self.assertIn('periods', result.keys())
        self.assertIn('day_types', result.keys())
        self.assertIn('days', result.keys())

        for key in result:
            self.assertIsInstance(result[key], Search)
