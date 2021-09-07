import json
from unittest import mock

from django.urls import reverse

from esapi.errors import ESQueryStopPatternTooShort, ESQueryResultEmpty, ESQueryDateRangeParametersDoesNotExist
from testhelper.helper import TestHelper


class MatchedStopDataTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:matchedStopData')
        self.data = {
            'term': 'term'
        }
        self.available_route = '506 00I'

    @mock.patch('esapi.helper.stop.ESStopHelper.get_matched_stop_list')
    def test_exec_elasticsearch_query_get(self, get_matched_stop_list):
        get_matched_stop_list.return_value = [('text', 'text_id')]
        expected = {
            "items": [{
                "text": "text",
                "id": "text_id"
            }]
        }
        response = self.client.get(self.url, self.data)
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.stop.ESStopHelper.get_matched_stop_list')
    def test_exec_elasticsearch_query_get_with_short_pattern(self, get_matched_stop_list):
        get_matched_stop_list.return_value = [('text', 'text_id')]
        data = {
            'term': ''
        }
        response = self.client.get(self.url, data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryStopPatternTooShort().get_status_response())


class StopInfoTest(TestHelper):
    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:stopInfo')
        self.data = {
            'stop': 'PA1',
            'date': '2020-06-07'
        }

    @mock.patch('esapi.helper.stop.ESStopHelper.get_stop_info')
    def test_exec_elasticsearch_query_get(self, get_stop_info):
        stop_dict = {
            "authCode": "T-20-68-NS-5",
            "latitude": -33.44012613,
            "longitude": -70.68002548,
            "name": "Parada 6 / (M) Quinta Normal",
            "startDate": "2020-06-27T00:00:00.000Z"
        }
        get_stop_info.return_value = stop_dict
        expected = {
            "info": [stop_dict]
        }
        response = self.client.get(self.url, self.data)
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.stop.ESStopHelper.get_stop_info')
    def test_exec_elasticsearch_query_get_with_wrong_date(self, get_stop_info):
        get_stop_info.side_effect = ESQueryResultEmpty
        data = {
            'term': ''
        }
        response = self.client.get(self.url, data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateRangeParametersDoesNotExist().get_status_response())
