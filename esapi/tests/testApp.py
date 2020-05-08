from django.apps import apps
from django.test import TestCase

from esapi.apps import EsapiConfig


class DatamanagerConfigConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(EsapiConfig.name, 'esapi')
        self.assertEqual(apps.get_app_config('esapi').name, 'esapi')
