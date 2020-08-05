import json
from unittest import mock

from django.urls import reverse
from elasticsearch_dsl import AttrList, AttrDict

from esapi.errors import ESQueryDateParametersDoesNotExist, ESQueryAuthRouteCodeTranslateDoesNotExist
from localinfo.models import OPDictionary
from testhelper.helper import TestHelper


class OPDataByAuthRouteCode(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods']

    def setUp(self):
        auth_code = 'T101 00I'
        op_code = '101I'
        OPDictionary.objects.create(auth_route_code=auth_code, op_route_code=op_code)
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:opdataAuthRoute')
        self.data = {}

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRouteCode'] = '100000'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    def test_wrong_auth_code(self):
        self.data['dates'] = '[["2020-03-05"]]'
        self.data['authRouteCode'] = '100000'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryAuthRouteCodeTranslateDoesNotExist('100000').get_status_response())

    @mock.patch('esapi.views.opdata.ESOPDataHelper')
    def test_correct_auth_code(self, helper):
        helper.return_value = helper
        helper.get_route_info.return_value = helper
        unsorted_dict = [AttrDict({'timePeriod': 2}), AttrDict({'timePeriod': 1})]
        helper.execute.return_value = [AttrDict({'dayType': AttrList(unsorted_dict)})]
        self.data['dates'] = '[["2020-03-05"]]'
        self.data['authRouteCode'] = 'T101 00I'
        response = self.client.get(self.url, self.data)
        expected_dict = '[{"timePeriod": "Pre nocturno"}, {"timePeriod": "Nocturno"}]'
        self.assertEqual(expected_dict, json.dumps(json.loads(response.content)['data']))
