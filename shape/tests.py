from mock import patch
from testhelper.helper import TestHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    @patch('shape.views.ESShapeHelper')
    @patch('shape.views.ESStopByRouteHelper')
    def test_site_route(self, es_stop_by_route_helper, es_shape_helper):
        es_shape_helper.return_value = es_shape_helper
        es_shape_helper.get_route_shape.return_value = dict(points=[])
        es_stop_by_route_helper.return_value = es_stop_by_route_helper
        es_stop_by_route_helper.get_stop_list.return_value = dict(stops=[])
        data = dict(route='abc', operationProgramDate='abc')
        self.check_json_response(self.client, 'shape:route', 200, data)

    def test_site_route_without_route_param(self):
        data = dict(operationProgramDate='abc')
        self.check_json_response(self.client, 'shape:route', 200, data)
        # json_response = self.check_json_response(self.client, 'shape:route', 200, data)
        # answer = json_response['status']
        # print(answer)
        # self.assertDictEqual(answer, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_site_route_without_operation_program_date_param(self):
        data = dict(route='abc')
        self.check_json_response(self.client, 'shape:route', 200, data)
        # json_response = self.check_json_response(self.client, 'shape:route', 200, data)
        # answer = json_response['status']
        # self.assertDictEqual(answer, ESQueryDateParametersDoesNotExist().get_status_response())

    def test_site_base(self):
        data = dict(route='', operationProgramDate='')
        self.check_http_response(self.client, 'shape:base', 200, data)

    def test_site_map(self):
        self.check_http_response(self.client, 'shape:map', 200)
