from django.apps import apps
from django.test import TestCase

from awsbackup.apps import AwsbackupConfig
from testhelper.helper import TestHelper


class AwsbackupConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AwsbackupConfig.name, 'awsbackup')
        self.assertEqual(apps.get_app_config('awsbackup').name, 'awsbackup')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_gps(self):
        self.check_http_response(self.client, 'awsbackup:gps', 200)

    def test_site_trip(self):
        self.check_http_response(self.client, 'awsbackup:trip', 200)

    def test_site_opprogram(self):
        self.check_http_response(self.client, 'awsbackup:opprogram', 200)

    def test_site_representativeweek(self):
        self.check_http_response(self.client, 'awsbackup:representativeweek', 200)

    def test_site_196(self):
        self.check_http_response(self.client, 'awsbackup:196', 200)

    def test_site_profile(self):
        self.check_http_response(self.client, 'awsbackup:profile', 200)

    def test_site_stage(self):
        self.check_http_response(self.client, 'awsbackup:stage', 200)

    def test_site_transaction(self):
        self.check_http_response(self.client, 'awsbackup:transaction', 200)

    def test_site_opspeed(self):
        self.check_http_response(self.client, 'awsbackup:opspeed', 200)

    def test_site_stoptime(self):
        self.check_http_response(self.client, 'awsbackup:stoptime', 200)

    def test_site_activeDownloadLink(self):
        self.check_http_response(self.client, 'awsbackup:activeDownloadLink', 200)
