# -*- coding: utf-8 -*-
from django.apps import apps
from django.test import TestCase

from consistencychecker.apps import ConsistencycheckerConfig
from testhelper.helper import TestHelper


class ConsistencycheckerConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ConsistencycheckerConfig.name, 'consistencychecker')
        self.assertEqual(apps.get_app_config('consistencychecker').name, 'consistencychecker')

class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_operator(self):
        self.check_http_response(self.client, 'consistencychecker:concistency', 200)

    def test_data_request(self):
        self.check_http_response(self.client, 'consistencychecker:getConsistencyData', 200)
