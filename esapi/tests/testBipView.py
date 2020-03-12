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

    @mock.patch('esapi.helper.bip.ESBipHelper.get_available_days')
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

    # @mock.patch('esapi.helper.bip.ESBipHelper.get_available_days')
    # @mock.patch('esapi.helper.basehelper.Search')
    # def test_exec_elasticsearch_query_with_result(self, es_query,
    #                                               operator_list):
    #     operator_list.return_value = []
    #     es_query_instance = es_query.return_value
    #     es_query_instance.filter.return_value = es_query_instance
    #     es_query_instance.query.return_value = es_query_instance
    #     es_query_instance.source.return_value = es_query_instance
    #     es_query_instance.scan.return_value = es_query_instance
    #     es_query_instance.execute = es_query_instance
    #     hit = mock.Mock()
    #     es_query_instance.aggregations.histogram.return_value = [hit]
    #     data = {
    #         'dates': '[["2018-01-01"]]'
    #     }
    #     response = self.client.get(self.url, data)
    #     print(response.content)
