# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.urls import reverse

from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableStatisticDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.resume.ESResumeStatisticHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
        answer = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, answer)


class GlobalDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:resumeData')
        self.data = {
            'dates': '[["2019-01-01", "2019-02-01"]]',
            'metrics[]': ['transactionNumber', 'smartcardNumber'],
        }
        self.available_date = '2019-01-01'

    @mock.patch('esapi.helper.resume.ESResumeStatisticHelper.get_data')
    def test_exec_elasticsearch_query_get(self, get_data):
        es_query = mock.Mock()
        hit = mock.Mock()
        hit.to_dict.return_value = {
            'date': '2019-10-22',
            'transactionWithoutRoute': 0,
            'smartcardNumber': 0
        }
        es_query.scan.return_value = [hit]
        get_data.return_value = es_query
        response = self.client.get(self.url, self.data)
        self.assertNotContains(response, 'status')
