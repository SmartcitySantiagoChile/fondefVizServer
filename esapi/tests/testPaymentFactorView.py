import json
from unittest import mock

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
        self.data['dates'] = '[[]]'
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

    @mock.patch('esapi.views.paymentfactor.PaymentFactorData.transform_es_answer')
    @mock.patch('esapi.helper.paymentfactor.ESPaymentFactorHelper.get_data')
    def test_exec_elasticsearch_query_with_result(self, operator_data, data):
        operator_data.return_value = ''
        data.return_value = {u'rows': [
            {'total': 4686.0, 'operator_id': 1, 'factor_by_date': [(1561939200000, 0.0)], 'assignation': u'VISITANTE',
             'factor_average': 0.0, 'sum': 0.0, 'neutral': 4686.0,
             'bus_station_name': u'Parada 2 / (M) Estaci\xf3n Central', 'day_type': u'Laboral', 'operator': u'Alsacia',
             'bus_station_id': u'365', 'subtraction': 0.0},
        ]}

        data = {
            'dates': '[["2018-01-01"]]'
        }
        expected = {"rows": [
            {"bus_station_name": "Parada 2 / (M) Estaci\u00f3n Central", "factor_by_date": [[1561939200000, 0.0]],
             "subtraction": 0.0, "neutral": 4686.0, "operator_id": 1, "day_type": "Laboral", "operator": "Alsacia",
             "bus_station_id": "365", "total": 4686.0, "assignation": "VISITANTE", "sum": 0.0, "factor_average": 0.0}]}

        response = self.client.get(self.url, data)
        self.assertDictEqual(json.loads(response.content), expected)
