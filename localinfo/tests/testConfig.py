from django.test import TestCase
from localinfo.apps import LocalinfoConfig
from django.apps import apps


class LocalInfoConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(LocalinfoConfig.name, 'localinfo')
        self.assertEqual(apps.get_app_config('localinfo').name, 'localinfo')
