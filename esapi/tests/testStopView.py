# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse

from esapi.errors import ESQueryStopPatternTooShort
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
