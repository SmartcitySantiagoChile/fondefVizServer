from django.apps import apps
from django.test import TestCase

from datamanager.apps import DatamanagerConfig
from testhelper.helper import TestHelper


class DatamanagerConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(DatamanagerConfig.name, 'datamanager')
        self.assertEqual(apps.get_app_config('datamanager').name, 'datamanager')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_loadmanager(self):
        self.check_http_response(self.client, 'datamanager:loadmanager', 200)

    def test_site_loadmanagerOp(self):
        self.check_http_response(self.client, 'datamanager:loadmanagerOP', 200)

    def test_data_jobHistoryByUser(self):
        self.check_http_response(self.client, 'datamanager:jobHistoryByUser', 200)
