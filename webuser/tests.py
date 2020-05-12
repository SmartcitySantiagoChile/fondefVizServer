from django.apps import apps
from django.test import TestCase

from webuser.apps import WebuserConfig


class WebuserConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(WebuserConfig.name, 'webuser')
        self.assertEqual(apps.get_app_config('webuser').name, 'webuser')
