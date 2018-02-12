# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from mock import mock

from esapi.tests.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, ESQueryResultEmpty

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
            'dayType': '',
            'period': '',
            'halfHour': ''
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
