import json
from unittest import mock

from django.urls import reverse

from esapi.errors import ESQueryResultEmpty, ESQueryDateParametersDoesNotExist
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableStageDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.stage.ESStageHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        expected = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, expected)


class PostProductTransfersDataTest(TestHelper):
    fixtures = ['daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:stageTransfers')
        self.data = {
            'dates': "[['']]",
            'dayType[]': [],
            'communes[]': []
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('datamanager.helper.ExporterManager.export_data')
    @mock.patch('esapi.helper.stage.ESStageHelper.get_post_products_aggregated_transfers_data_query')
    def test_exec_elasticsearch_query_get_with_aggregation_data(self,
                                                                get_post_products_aggregated_transfers_data_query, export_data):
        get_post_products_aggregated_transfers_data_query.return_value = mock.Mock()
        export_data.return_value = mock.Mock()
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': [],
            'communes[]': [],
            'exportButton2': True,
        }
        status = ExporterDataHasBeenEnqueuedMessage().get_status_response()
        response = self.client.post(self.url, data)
        self.assertJSONEqual(json.dumps(json.loads(response.content)['status']), status)

    @mock.patch('datamanager.helper.ExporterManager.export_data')
    @mock.patch('esapi.helper.stage.ESStageHelper.get_post_products_transfers_data_query')
    def test_exec_elasticsearch_query_get(self, get_post_products_transfers_data_query, export_data):
        get_post_products_transfers_data_query.return_value = mock.Mock()
        export_data.return_value = mock.Mock()
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': [],
            'communes[]': [],
        }
        status = ExporterDataHasBeenEnqueuedMessage().get_status_response()
        response = self.client.post(self.url, data)
        self.assertJSONEqual(json.dumps(json.loads(response.content)['status']), status)

