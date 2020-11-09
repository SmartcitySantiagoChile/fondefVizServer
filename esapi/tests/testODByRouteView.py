# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse

from esapi.errors import ESQueryDateParametersDoesNotExist
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableODDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        answer = {
            'info': [],
            'availableDays': [self.available_date]
        }
        self.assertJSONEqual(response.content, answer)


class AvailableRoutesTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableODRoutes')
        self.data = {}
        self.available_route = '506 00I'

    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_available_routes')
    def test_ask_for_routes_with_data(self, get_available_routes):
        available_days = {'Metbus': {'506': [self.available_route]}}
        get_available_routes.return_value = (available_days, [])
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        expected = {
            "routesDict": {},
            'availableRoutes': {
                'Metbus': {
                    '506': [self.available_route]
                }
            },
            'operatorDict': [],
            'opProgramDates': {}
        }
        self.assertJSONEqual(response.content, expected)


class ODMatrixDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:ODMatrixData')
        self.data = {
            'dates': '',
            'authRoute': '',
            'dayType[]': [],
            'period[]': []
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper.get_od_data')
    @mock.patch('esapi.views.odbyroute.check_operation_program')
    def test_exec_elasticsearch_query_get(self, check_operation_program, get_od_data, get_stop_list):
        get_stop_list.return_value = {'stops': []}
        check_operation_program.return_value = None
        get_od_data.return_value = ([], 0)
        data = {
            'dates': '[["2018-01-01"]]',
            'authRoute': '506 00I',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3]
        }
        expected = {
            "data": {
                "stopList": [],
                "matrix": [],
                "maximum": 0
            }
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.odbyroute.ExporterManager')
    @mock.patch('esapi.views.odbyroute.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())
