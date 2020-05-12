from django.apps import apps
from django.test import TestCase

from globalstat.apps import GlobalstatConfig
from testhelper.helper import TestHelper


class GlobalstatConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(GlobalstatConfig.name, 'globalstat')
        self.assertEqual(apps.get_app_config('globalstat').name, 'globalstat')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_resume(self):
        self.check_http_response(self.client, 'globalstat:resume', 200)

    def test_site_detail(self):
        self.check_http_response(self.client, 'globalstat:detail', 200)
