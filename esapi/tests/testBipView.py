# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse

from esapi.errors import ESQueryResultEmpty
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableBipDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.bip.ESBipHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        answer = {
            'info': [],
            'availableDays': [self.available_date]
        }
        self.assertJSONEqual(response.content, answer)


class LoadBipTransactionByOperatorData(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:operatorBipData')
        self.data = {
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.profile.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())