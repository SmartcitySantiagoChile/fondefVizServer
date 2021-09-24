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

    def test_site_transfers(self):
        self.check_http_response(self.client, 'postproducts:transfers', 200)

    def test_site_trip_between_zones(self):
        self.check_http_response(self.client, 'postproducts:tripsBetweenZones', 200)

    def test_site_boarding_and_alighting_by_zone(self):
        self.check_http_response(self.client, 'postproducts:boardingAndAlightingByZone', 200)

    def test_site_transactions_by_operator(self):
        self.check_http_response(self.client, 'postproducts:transactionsByOperator', 200)
