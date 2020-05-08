from unittest import mock

from django.apps import apps
from django.test import TestCase
from django.urls import reverse

from awsbackup.apps import AwsbackupConfig
from testhelper.helper import TestHelper


class AwsbackupConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AwsbackupConfig.name, 'awsbackup')
        self.assertEqual(apps.get_app_config('awsbackup').name, 'awsbackup')


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_gps(self, awsession):
        url = reverse('awsbackup:gps')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_trip(self, awsession):
        url = reverse('awsbackup:trip')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_opprogram(self, awsession):
        url = reverse('awsbackup:opprogram')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_representativeweek(self, awsession):
        url = reverse('awsbackup:representativeweek')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_196(self, awsession):
        url = reverse('awsbackup:196')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_profile(self, awsession):
        url = reverse('awsbackup:profile')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_stage(self, awsession):
        url = reverse('awsbackup:stage')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_transaction(self, awsession):
        url = reverse('awsbackup:transaction')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_opspeed(self, awsession):
        url = reverse('awsbackup:opspeed')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_stoptime(self, awessesion):
        url = reverse('awsbackup:stoptime')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.aws.AWSSession')
    def test_site_activeDownloadLink(self, awsession):
        url = reverse('awsbackup:activeDownloadLink')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')
