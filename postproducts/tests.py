from django.apps import apps
from django.test import TestCase

from testhelper.helper import TestHelper
from postproducts.apps import PostproductsConfig


class PostproductsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(PostproductsConfig.name, 'postproducts')
        self.assertEqual(apps.get_app_config('postproducts').name, 'postproducts')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_from_to_map(self):
        self.check_http_response(self.client, 'postproducts:transfers', 200)

    def test_site_large_trips(self):
        self.check_http_response(self.client, 'postproducts:tripsBetweenZones', 200)

    def test_site_map(self):
        self.check_http_response(self.client, 'postproducts:boardingAndAlightingByZone', 200)
