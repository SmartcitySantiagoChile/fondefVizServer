# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from mock import mock

from esapi.tests.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist

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

    def test_wrong_parameter(self):
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())

    @mock.patch('elasticsearch_dsl.Search')
    def test_asd(self, es_query):
        es_query.scan.return_value = []

        response = self.client.get(self.url, self.data)
        print(response.content)

        es_query.scan.assert_called_once()
