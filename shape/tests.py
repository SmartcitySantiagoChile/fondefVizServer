from django.apps import apps
from django.test import TestCase

from shape.apps import ShapeConfig
from testhelper.helper import TestHelper


class ShapeConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ShapeConfig.name, 'shape')
        self.assertEqual(apps.get_app_config('shape').name, 'shape')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_map(self):
        self.check_http_response(self.client, 'shape:map', 200)
