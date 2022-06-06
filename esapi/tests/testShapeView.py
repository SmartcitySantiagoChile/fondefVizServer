import json
from unittest import mock
from unittest.mock import patch

from django.urls import reverse

from esapi.errors import ESQueryStopPatternTooShort
from localinfo.models import OPDictionary, OPProgram
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

    def test_site_route_without_operation_program_date_param(self):
        data = dict(route='abc')
        self.check_json_response(self.client, 'esapi:shapeRoute', 200, data)

    def test_site_base(self):
        op_program_obj = OPProgram.objects.create(valid_from='2020-01-01')
        records = [
            ['101', 'F41 00I', 'F41I'],
            ['101', 'F41 00R', 'F41R'],
            ['101', 'F41 06I', 'F41I'],
            ['101', 'F41 06R', 'F41R'],
            ['101', 'F41 08I', 'F41I'],
            ['102', 'F72 00I', 'F72I'],
            ['102', 'F72 00R', 'F72R'],
            ['102', 'F72 06R', 'F72R'],
            ['103', 'T463 00I', '463I'],
            ['103', 'T463 00R', '463R'],
            ['103', 'T463 06R', '463R'],
            ['103', 'T463 07I', '463I'],
            ['104', 'F74 00I', 'F74I'],
            ['104', 'F74 00R', 'F74R'],
            ['104', 'F74 01I', 'F74I'],
            ['104', 'F74 07I', 'F74I'],
            ['105', 'B85 00I', 'B85I'],
            ['105', 'B85 00R', 'B85R'],
            ['105', 'B85 05R', 'B85R'],
            ['106', 'F46 00I', 'F46I'],
        ]
        for data in records:
            OPDictionary.objects.create(auth_route_code=data[1], op_route_code=data[2], user_route_code=data[0],
                                        route_type='a', op_program=op_program_obj)

        response = self.check_http_response(self.client, 'esapi:shapeBase', 200)
        json_response = json.loads(response.content)
        expected_value = {
            'dates': ['2020-01-01'],
            'dates_periods_dict': {'2020-01-01': 1},
            'periods': {'1': [], '2': [], '3': [], '4': [], '5': []},
            'op_routes_dict': {
                '2020-01-01': {
                    '101': {'F41 00I': 'F41I', 'F41 00R': 'F41R', 'F41 06I': 'F41I', 'F41 06R': 'F41R',
                            'F41 08I': 'F41I'},
                    '102': {'F72 00I': 'F72I', 'F72 00R': 'F72R', 'F72 06R': 'F72R'},
                    '103': {'T463 00I': '463I', 'T463 00R': '463R', 'T463 06R': '463R', 'T463 07I': '463I'},
                    '104': {'F74 00I': 'F74I', 'F74 00R': 'F74R', 'F74 01I': 'F74I', 'F74 07I': 'F74I'},
                    '105': {'B85 00I': 'B85I', 'B85 00R': 'B85R', 'B85 05R': 'B85R'},
                    '106': {'F46 00I': 'F46I'}
                }
            }
        }

        self.assertDictEqual(json_response, expected_value)

    @patch('esapi.views.shape.ESProfileHelper')
    @patch('esapi.views.shape.ESShapeHelper')
    @patch('esapi.views.shape.ESStopByRouteHelper')
    def test_GetUserRoutesByOP(self, es_stop_by_route_helper, es_shape_helper, es_profile_helper):
        op_days = ['2017-03-01', '2018-03-01', '2018-07-01', '2019-03-01', '2019-04-01', '2019-07-01', '2019-10-12',
                   '2020-03-02', '2020-06-27']

        es_shape_helper.return_value = es_shape_helper
        es_shape_helper.get_available_days.return_value = op_days[:5]

        es_stop_by_route_helper.return_value = es_stop_by_route_helper
        es_stop_by_route_helper.get_available_days.return_value = op_days[5:]

        es_profile_helper.return_value = es_profile_helper
        es_profile_helper.get_available_routes.return_value = [[], []]

        data = {
            'op_program': '2020-03-02'
        }
        self.client.get(reverse('esapi:shapeUserRoutes'), data)
