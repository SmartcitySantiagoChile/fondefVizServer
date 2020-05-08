from django.apps import apps
from django.test import TestCase

from speed.apps import SpeedConfig
from testhelper.helper import TestHelper


class VelocityConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(SpeedConfig.name, 'speed')
        self.assertEqual(apps.get_app_config('speed').name, 'speed')

class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_matrix(self):
        self.check_http_response(self.client, 'speed:matrix', 200)

    def test_site_ranking(self):
        self.check_http_response(self.client, 'speed:ranking', 200)

    def test_site_variation(self):
        self.check_http_response(self.client, 'speed:variation', 200)
