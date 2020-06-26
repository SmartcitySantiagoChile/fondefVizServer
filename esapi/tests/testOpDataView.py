# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.urls import reverse

from esapi.errors import ESQueryDateParametersDoesNotExist, ESQueryAuthRouteCodeTranslateDoesNotExist
from localinfo.models import OPDictionary
from testhelper.helper import TestHelper


class OPDataByAuthRouteCode(TestHelper):

    def setUp(self):
        auth_code = 'T101 00I'
        op_code = '101I'
        OPDictionary.objects.create(auth_route_code=auth_code, op_route_code=op_code)
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:opdataAuthRoute')
        self.data = {
        }

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
