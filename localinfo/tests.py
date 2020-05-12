# -*- coding: utf-8 -*-
from django.apps import apps
from django.test import TestCase

from localinfo.apps import LocalinfoConfig


class LocalInfoConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(LocalinfoConfig.name, 'localinfo')
        self.assertEqual(apps.get_app_config('localinfo').name, 'localinfo')
