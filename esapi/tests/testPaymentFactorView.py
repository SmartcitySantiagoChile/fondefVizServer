# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse

from esapi.errors import ESQueryResultEmpty, ESQueryDateParametersDoesNotExist
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availablePaymentfactorDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.paymentfactor.ESPaymentFactorHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        expected = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, expected)


class PaymentFactorDataTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:paymentfactorData')
        self.data = {
            'dates': '[[]]',
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        self.data['dates'] = '[]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.paymentfactor.ESPaymentFactorHelper.get_available_days')
    @mock.patch('esapi.helper.basehelper.Search')
    def test_exec_elasticsearch_query_without_result(self, es_query,
                                                     operator_list):
        operator_list.return_value = []
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []
        data = {
            'dates': '[["2018-01-01"]]'
        }
        response = self.client.get(self.url, data)
        print(response.content)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.paymentfactor.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager_instance = exporter_manager.return_value
        exporter_manager_instance.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())
