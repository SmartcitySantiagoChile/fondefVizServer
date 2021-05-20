import json
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from elasticsearch_dsl import AttrList, AttrDict

from esapi.errors import ESQueryDateParametersDoesNotExist, ESQueryResultEmptyRoute
from localinfo.models import OPDictionary, OPProgram
from testhelper.helper import TestHelper


class OPDataByOPRouteCode(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods']

    def setUp(self):
        self.op_program = OPProgram.objects.create(valid_from='2020-01-01')
        time_at = timezone.now()
        auth_code = 'T101 00I'
        op_route_code = '101I'
        route_type = '101 Ida'
        self.op_dictionary = OPDictionary.objects.create(auth_route_code=auth_code, route_type=route_type,
                                                         op_route_code=op_route_code, user_route_code=auth_code,
                                                         created_at=time_at, op_program=self.op_program)
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:opdataAuthRoute')
        self.data = {}

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['opRouteCode'] = '100000'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.views.opdata.ESOPDataHelper')
    def test_wrong_op_code(self, helper):
        self.data['dates'] = '[["2020-01-01"]]'
        self.data['opRouteCode'] = '100000'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmptyRoute('100000').get_status_response())
        helper.assert_called_once()

    @mock.patch('esapi.views.opdata.ESOPDataHelper')
    def test_correct_op_route_code(self, helper):
        helper.return_value = helper
        helper.get_route_info.return_value = helper
        unsorted_dict = [AttrDict({'timePeriod': 2}), AttrDict({'timePeriod': 1})]
        helper.execute.return_value = [AttrDict({'dayType': AttrList(unsorted_dict)})]
        self.data['dates'] = '[["2020-01-01"]]'
        self.data['opRouteCode'] = '101I'
        response = self.client.get(self.url, self.data)
        expected_dict = '{"1": {"timePeriod": "Pre nocturno (00:00:00-00:59:59)"}, "2": {"timePeriod": "Nocturno (01:00:00-05:29:59)"}}'
        self.assertEqual(expected_dict, json.dumps(json.loads(response.content)['data']))
