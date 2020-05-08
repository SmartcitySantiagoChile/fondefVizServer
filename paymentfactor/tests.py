from django.apps import apps
from django.test import TestCase

from paymentfactor.apps import PaymentfactorConfig
from testhelper.helper import TestHelper


class PaymentfactorConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(PaymentfactorConfig.name, 'paymentfactor')
        self.assertEqual(apps.get_app_config('paymentfactor').name, 'paymentfactor')



class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_operator(self):
        self.check_http_response(self.client, 'paymentfactor:index', 200)
