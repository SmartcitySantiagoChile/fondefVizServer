# -*- coding: utf-8 -*-
from django.apps import apps
from django.test import TestCase

from bowerapp.apps import BowerappConfig


class BowerappConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(BowerappConfig.name, 'bowerapp')
        self.assertEqual(apps.get_app_config('bowerapp').name, 'bowerapp')
