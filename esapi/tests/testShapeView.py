# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock
from django.urls import reverse
from mock import patch

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


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    @patch('esapi.views.shape.ESShapeHelper')
    @patch('esapi.views.shape.ESStopByRouteHelper')
    def test_site_route(self, es_stop_by_route_helper, es_shape_helper):
        es_shape_helper.return_value = es_shape_helper
        es_shape_helper.get_route_shape.return_value = dict(points=[])
        es_stop_by_route_helper.return_value = es_stop_by_route_helper
        es_stop_by_route_helper.get_stop_list.return_value = dict(stops=[])
        data = dict(route='abc', operationProgramDate='abc')
        self.check_json_response(self.client, 'esapi:shapeRoute', 200, data)

    def test_site_route_without_route_param(self):
        data = dict(operationProgramDate='abc')
        self.check_json_response(self.client, 'esapi:shapeRoute', 200, data)
        # json_response = self.check_json_response(self.client, 'shape:route', 200, data)
        # answer = json_response['status']
        # print(answer)
        # self.assertDictEqual(answer, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_site_route_without_operation_program_date_param(self):
        data = dict(route='abc')
        self.check_json_response(self.client, 'esapi:shapeRoute', 200, data)
        # json_response = self.check_json_response(self.client, 'shape:route', 200, data)
        # answer = json_response['status']
        # self.assertDictEqual(answer, ESQueryDateParametersDoesNotExist().get_status_response())

    @patch('esapi.views.shape.ESShapeHelper')
    @patch('esapi.views.shape.ESStopByRouteHelper')
    def test_site_base(self, es_stop_by_route_helper, es_shape_helper):
        es_shape_helper.return_value = es_shape_helper
        es_shape_helper.get_route_shape.return_value = dict(points=[])
        es_stop_by_route_helper.return_value = es_stop_by_route_helper
        es_stop_by_route_helper.get_stop_list.return_value = dict(stops=[])
        data = dict(route='', operationProgramDate='')
        self.check_http_response(self.client, 'esapi:shapeBase', 200, data)