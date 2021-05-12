import json
from unittest import mock

from django.urls import reverse

from esapi.errors import ESQueryResultEmpty, ESQueryDateParametersDoesNotExist
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
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.views.bip.ExporterManager')
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
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.bip.BipTransactionByOperatorData.transform_es_answer')
    @mock.patch('esapi.helper.bip.ESBipHelper.get_bip_by_operator_data')
    def test_exec_elasticsearch_query_with_result(self, operator_data, data):
        operators_data = [{u'item': u'Alsacia', u'value': 1}, {u'item': u'Su Bus', u'value': 2},
                          {u'item': u'Buses Vule', u'value': 3}, {u'item': u'Express', u'value': 4},
                          {u'item': u'Buses Metropolitana', u'value': 5}, {u'item': u'Red Bus Urbano', u'value': 6},
                          {u'item': u'STP Santiago', u'value': 7}, {u'item': u'Metro', u'value': 8},
                          {u'item': u'Metrotren', u'value': 9}]
        histogram = [{u'operators': {
            u'buckets': [{u'key': 8, u'doc_count': 2828267}, {u'key': 5, u'doc_count': 644126},
                         {u'key': 3, u'doc_count': 625541}, {u'key': 4, u'doc_count': 621139},
                         {u'key': 2, u'doc_count': 464614}, {u'key': 6, u'doc_count': 349488},
                         {u'key': 7, u'doc_count': 275174}, {u'key': 9, u'doc_count': 83963}],
            u'sum_other_doc_count': 0, u'doc_count_error_upper_bound': 0}, u'key_as_string': u'2019-10-07 00:00:00',
            u'key': 1570406400000, u'doc_count': 5892312}]

        operator_data.return_value = ['', operators_data]
        data.return_value = histogram
        data = {
            'dates': '[["2019-10-07"]]'
        }
        response = self.client.get(self.url, data)
        expected = {"operators": [{"item": "Alsacia", "value": 1}, {"item": "Su Bus", "value": 2},
                                  {"item": "Buses Vule", "value": 3}, {"item": "Express", "value": 4},
                                  {"item": "Buses Metropolitana", "value": 5}, {"item": "Red Bus Urbano", "value": 6},
                                  {"item": "STP Santiago", "value": 7}, {"item": "Metro", "value": 8},
                                  {"item": "Metrotren", "value": 9}], "data": [{"operators": {
            "buckets": [{"key": 8, "doc_count": 2828267}, {"key": 5, "doc_count": 644126},
                        {"key": 3, "doc_count": 625541}, {"key": 4, "doc_count": 621139},
                        {"key": 2, "doc_count": 464614}, {"key": 6, "doc_count": 349488},
                        {"key": 7, "doc_count": 275174}, {"key": 9, "doc_count": 83963}],
            "doc_count_error_upper_bound": 0, "sum_other_doc_count": 0}, "key_as_string": "2019-10-07 00:00:00",
            "key": 1570406400000,
            "doc_count": 5892312}]}
        self.assertDictEqual(json.loads(response.content), expected)
