# -*- coding: utf-8 -*-


from django.test import TestCase
from django.urls import reverse

from mock import mock

from esapi.helper.profile import ESProfileHelper
from elasticsearch_dsl import Search
from esapi.tests.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryResultEmpty, ESQueryStopParameterDoesNotExist, ESQueryStopPatternTooShort

from localinfo.models import Operator

import json
import builtins


class ESProfileIndexTest(TestCase):

    def setUp(self):
        self.instance = ESProfileHelper()

    def test_ask_for_base_params(self):
        result = self.instance.get_base_params()

        self.assertIn('periods', list(result.keys()))
        self.assertIn('day_types', list(result.keys()))
        self.assertIn('days', list(result.keys()))

        for key in result:
            self.assertIsInstance(result[key], Search)

    def test_ask_for_profile_by_stop(self):
        start_date = ''
        end_date = ''
        day_type = ['LABORAL']
        stop_code = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]

        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_profile_by_stop_data, start_date, end_date,
                          day_type, stop_code, period, half_hour)
        stop_code = 'PA433'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_stop_data, start_date,
                          end_date, day_type, stop_code, period, half_hour)
        start_date = '2018-01-01'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_stop_data, start_date,
                          end_date, day_type, stop_code, period, half_hour)
        end_date = '2018-01-02'
        result = self.instance.get_profile_by_stop_data(start_date, end_date, day_type, stop_code, period, half_hour)

        self.assertIsInstance(result, Search)

    @mock.patch('esapi.helper.profile.ElasticSearchHelper.make_multisearch_query_for_aggs')
    def test_ask_for_stop(self, mock_method):
        mock_method.return_value = {'1': [], '2': [], '3': []}
        term = ''
        result = self.instance.get_matched_stop_list(term)

        self.assertIn('1', list(result.keys()))
        self.assertIn('2', list(result.keys()))
        self.assertIn('3', list(result.keys()))
        for key in result:
            self.assertIsInstance(result[key], list)

    @mock.patch('esapi.helper.profile.ElasticSearchHelper.make_multisearch_query_for_aggs')
    def test_ask_for_available_days(self, mock_method):
        mock_method.return_value = {'days': []}

        result = self.instance.get_available_days()
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

        result, operator_list = self.instance.get_available_routes()

        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [{'id': 1, 'text': 'Metbus'}])

    def test_ask_for_profile_by_expedition(self):
        start_date = ''
        end_date = ''
        day_type = ['LABORAL']
        auth_route = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]

        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_profile_by_expedition_data, start_date,
                          end_date, day_type, auth_route, period, half_hour)
        auth_route = '506 00I'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_expedition_data,
                          start_date, end_date, day_type, auth_route, period, half_hour)
        start_date = '2018-01-01'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_expedition_data,
                          start_date, end_date, day_type, auth_route, period, half_hour)
        end_date = '2018-02-01'

        result = self.instance.get_profile_by_expedition_data(start_date, end_date, day_type, auth_route, period,
                                                              half_hour)
        self.assertIsInstance(result, Search)


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
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
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
        es_query_instance.scan.return_value = [item]

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
        es_query_instance.scan.assert_called_once()

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, es_query):
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []

        self.data['startDate'] = '2018-01-01'
        self.data['endDate'] = '2018-01-01'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)

        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        es_query_instance.scan.assert_called_once()


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
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
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
        es_query_instance.scan.return_value = [item]

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
        es_query_instance.scan.assert_called_once()

    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, es_query):
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []

        self.data['startDate'] = '2018-01-01'
        self.data['endDate'] = '2018-01-01'
        self.data['stopCode'] = '506 00I'
        response = self.client.get(self.url, self.data)

        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        es_query_instance.scan.assert_called_once()


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

    @mock.patch.object(__builtin__, 'dir')
    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result(self, es_multi_query, dir_mock):
        dir_mock.return_value = ['unique']
        es_multi_query_instance = es_multi_query.return_value
        es_multi_query_instance.add.return_value = es_multi_query_instance
        type(self.item).doc_count = 0
        es_multi_query_instance.execute.return_value = [self.item]

        self.data['term'] = 'PA4'
        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        es_multi_query_instance.execute.assert_called_once()

    @mock.patch.object(__builtin__, 'dir')
    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result_with_key_as_string(self, es_multi_query, dir_mock):
        dir_mock.return_value = ['unique']
        es_multi_query_instance = es_multi_query.return_value
        es_multi_query_instance.add.return_value = es_multi_query_instance

        type(self.item).doc_count = mock.PropertyMock(return_value=1)
        self.item.__iter__ = mock.Mock(return_value=iter(['key_as_string']))
        type(self.item).key_as_string = mock.PropertyMock(return_value='PA433')
        es_multi_query_instance.execute.return_value = [self.item]

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
        es_multi_query_instance.execute.assert_called_once()

    @mock.patch.object(__builtin__, 'dir')
    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_exec_elasticsearch_query_with_result_without_key_as_string(self, es_multi_query, dir_mock):
        dir_mock.return_value = ['unique']
        es_multi_query_instance = es_multi_query.return_value
        es_multi_query_instance.add.return_value = es_multi_query_instance
        type(self.item).doc_count = mock.PropertyMock(return_value=1)
        self.item.__iter__ = mock.Mock(return_value=iter([]))
        type(self.item).key = mock.PropertyMock(return_value='PA433')
        es_multi_query_instance.execute.return_value = [self.item]

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
        es_multi_query_instance.execute.assert_called_once()


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

    @mock.patch.object(__builtin__, 'dir')
    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_ask_for_days_with_data(self, es_multi_query, dir_mock):
        dir_mock.return_value = ['unique']
        es_multi_query_instance = es_multi_query.return_value
        es_multi_query_instance.add.return_value = es_multi_query_instance
        type(self.item).doc_count = 1
        es_multi_query_instance.execute.return_value = [self.item]

        response = self.client.get(self.url, self.data)

        self.assertNotContains(response, 'status')
        answer = {
            'availableDays': [self.available_date]
        }
        self.assertJSONEqual(response.content, answer)
        es_multi_query_instance.execute.assert_called_once()


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

    @mock.patch.object(__builtin__, 'dir')
    @mock.patch('esapi.helper.basehelper.Search')
    def test_ask_for_days_with_data(self, es_query, dir_mock):
        dir_mock.return_value = ['unique']
        es_query_instance = es_query.return_value
        es_query_instance.__getitem__.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        type(es_query_instance).aggs = mock.PropertyMock()
        es_query_instance.execute.return_value = self.item

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
        es_query_instance.execute.assert_called_once()
