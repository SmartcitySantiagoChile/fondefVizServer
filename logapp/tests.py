from django.apps import apps
from django.test import TestCase

from logapp.apps import LogappConfig


class LogappConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(LogappConfig.name, 'logapp')
        self.assertEqual(apps.get_app_config('logapp').name, 'logapp')
