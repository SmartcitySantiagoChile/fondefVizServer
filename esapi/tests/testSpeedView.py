# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse

from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist, ESQueryResultEmpty, \
    ESQueryDateParametersDoesNotExist
from esapi.messages import ExporterDataHasBeenEnqueuedMessage, SpeedVariationWithLessDaysMessage
from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableSpeedDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        answer = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, answer)


class AvailableRoutesTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableSpeedRoutes')
        self.data = {}
        self.available_route = '506 00I'

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_available_routes')
    def test_ask_for_routes_with_data(self, get_available_routes):
        available_days = {'Metbus': {'506': [self.available_route]}}
        get_available_routes.return_value = (available_days, [])
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        expected = {
            'availableRoutes': {
                'Metbus': {
                    '506': [self.available_route]
                }
            },
            'operatorDict': [],
            'routesDict': {},
            'opProgramDates': {}
        }
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_available_routes')
    def test_ask_for_routes_without_data(self, get_available_routes):
        get_available_routes.side_effect = ESQueryOperatorParameterDoesNotExist()
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryOperatorParameterDoesNotExist().get_status_response())
        self.assertContains(response, 'status')


class MatrixDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:matrixData')
        self.data = {
            'dates': '[[""]]',
            'authRoute': '',
            'dayType[]': [],
        }

    @mock.patch('esapi.views.speed.check_operation_program')
    def test_wrong_route(self, check_operation_program):
        check_operation_program.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_speed_data')
    @mock.patch('esapi.views.speed.check_operation_program')
    def test_exec_elasticsearch_query_get(self, check_operation_program, get_speed_data, get_route_shape):
        get_route_shape.return_value = get_route_shape
        get_route_shape.__getitem__.return_value = [{
            'latitude': 1,
            'longitude': 2,
            'segmentStart': 1
        }]
        check_operation_program.return_value = None
        get_speed_data.return_value = {}
        data = {
            'dates': '[["2018-01-01"]]',
            'authRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        expected = {"route": {"points": [[1, 2]], "start_end": [[0, 0]], "name": "506 00I"}, "segments": [0, 1],
                    "matrix": [[[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]],
                               [[0, -1, 0, 0, 0], [0, -1, 0, 0, 0]], ]}
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.speed.ExporterManager')
    @mock.patch('esapi.views.speed.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class RankingDataTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:rankingData')
        self.data = {
            'dates': '[[""]]',
            'authRoute': '',
            'dayType[]': [],
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_ranking_data')
    @mock.patch('esapi.views.speed.check_operation_program')
    def test_exec_elasticsearch_query_get(self, check_operation_program, get_ranking_data):
        check_operation_program.return_value = None
        get_ranking_data.return_value = ['data'] * 1001
        data = {
            'dates': '[["2018-01-01"]]',
            'authRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        expected = {
            "hours": ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
                      "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                      "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
                      "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
                      "22:00", "22:30", "23:00", "23:30"],
            "data": ["data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data", "data",
                     "data", "data", "data", "data"]}
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.speed.ExporterManager')
    @mock.patch('esapi.views.speed.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class SpeedByRouteTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:speedByRoute')
        self.data = {
            'dates': '[["2018-01-01"]]',
            'authRoute': '',
            'dayType[]': [],
        }

    @mock.patch('esapi.views.speed.check_operation_program')
    def test_wrong_route(self, check_operation_program):
        check_operation_program.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_wrong_start_date(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_detail_ranking_data')
    @mock.patch('esapi.views.speed.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_get(self, search, check_operation_program, get_detail_ranking_data,
                                          get_route_shape):
        search_instance = search.return_value
        search_instance.execute.return_value = search_instance
        type(search_instance).aggregations = mock.PropertyMock(return_value=search_instance)
        type(search_instance).sections = mock.PropertyMock(return_value=search_instance)
        sec = mock.Mock()
        type(sec).key = mock.PropertyMock(return_value='key')
        type(sec).speed = mock.PropertyMock(return_value=sec)
        type(sec).value = mock.PropertyMock(return_value=1)
        type(search_instance).buckets = mock.PropertyMock(return_value=[sec])
        get_route_shape.return_value = get_route_shape
        get_route_shape.__getitem__.return_value = [{
            'latitude': 1,
            'longitude': 2,
            'segmentStart': 1
        }]
        check_operation_program.return_value = None
        get_detail_ranking_data.return_value = search_instance
        data = {
            'dates': '[["2018-01-01"]]',
            'authRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        expected = {
            "route": {
                "points": [[1, 2]],
                "start_end": [[0, 0]],
                "name": "506 00I"
            },
            "speed": [0]
        }

        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.speed.ExporterManager')
    @mock.patch('esapi.views.speed.check_operation_program')
    @mock.patch('esapi.helper.speed.ESSpeedHelper.get_base_detail_ranking_data_query')
    def test_exec_elasticsearch_query_post(self, get_base_detail_ranking_data_query, check_operation_program,
                                           exporter_manager):
        get_base_detail_ranking_data_query.return_value = None
        check_operation_program.return_value = None
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class SpeedVariationTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:speedVariation')
        self.data = {
            'dates': '[[""]]',
            'authRoute': '',
            'dayType[]': [],
        }

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_most_recent_operation_program_date')
    @mock.patch('esapi.views.speed.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_with_result(self, search, check_operation_program,
                                                  get_most_recent_operation_program_date):
        search_instance = search.return_value
        search_instance.execute.return_value = search_instance
        search_instance.filter.return_value = search_instance
        search_instance.__getitem__.return_value = search_instance
        type(search_instance).aggregations = mock.PropertyMock(return_value=search_instance)
        type(search_instance).routes = mock.PropertyMock(return_value=search_instance)
        rou = mock.Mock()
        per = mock.Mock()
        day = mock.Mock()
        type(day).key = mock.PropertyMock(return_value=['*', '+'])
        type(day).time = mock.PropertyMock(return_value=day)
        type(day).speed = mock.PropertyMock(return_value=day)
        type(day).n_obs = mock.PropertyMock(return_value=day)
        type(day).stats = mock.PropertyMock(return_value=day)
        type(day).std_deviation = mock.PropertyMock(return_value=0)
        type(day).value = mock.PropertyMock(return_value=1)

        type(per).key = mock.PropertyMock(return_value='key2')
        type(per).days = mock.PropertyMock(return_value=per)
        type(per).buckets = mock.PropertyMock(return_value=[day])

        type(rou).key = mock.PropertyMock(return_value='key')
        type(rou).periods = mock.PropertyMock(return_value=rou)
        type(rou).buckets = mock.PropertyMock(return_value=[per])
        type(search_instance).buckets = mock.PropertyMock(return_value=[rou])
        get_most_recent_operation_program_date.return_value = '2018-01-01'
        check_operation_program.return_value = None
        data = {
            'dates': '[["2018-01-01"]]',
            'operator': 1,
            'userRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, SpeedVariationWithLessDaysMessage(0, '2018-01-01').get_status_response())

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_most_recent_operation_program_date')
    @mock.patch('esapi.views.speed.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, search, check_operation_program,
                                                     get_most_recent_operation_program_date):
        search_instance = search.return_value
        search_instance.execute.return_value = search_instance
        search_instance.filter.return_value = search_instance
        search_instance.__getitem__.return_value = search_instance
        type(search_instance).aggregations = mock.PropertyMock(return_value=search_instance)
        type(search_instance).routes = mock.PropertyMock(return_value=search_instance)
        type(search_instance).buckets = mock.PropertyMock(return_value=[])
        get_most_recent_operation_program_date.return_value = '2018-01-01'
        check_operation_program.return_value = None
        data = {
            'dates': '[["2018-01-01"]]',
            'operator': 1,
            'userRoute': '506 00I',
            'dayType[]': ['LABORAL'],
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_most_recent_operation_program_date')
    @mock.patch('esapi.views.speed.ExporterManager')
    @mock.patch('esapi.views.speed.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager,
                                           get_most_recent_operation_program_date):
        check_operation_program.return_value = None
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        get_most_recent_operation_program_date.return_value = '2019-01-01'
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['operator'] = '1'
        self.data['userRoute'] = '506 00I'
        self.data['dayType[]'] = ['LABORAL']
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())

    # TODO: reproducir los distintos casos para value - color en transform_data
