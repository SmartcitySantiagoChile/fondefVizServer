from unittest import mock

from django.urls import reverse

from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_gps(self, awsession):
        url = reverse('awsbackup:gps')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_trip(self, awsession):
        url = reverse('awsbackup:trip')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_opprogram(self, awsession):
        url = reverse('awsbackup:opprogram')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_representativeweek(self, awsession):
        url = reverse('awsbackup:representativeweek')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_196(self, awsession):
        url = reverse('awsbackup:196')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_profile(self, awsession):
        url = reverse('awsbackup:profile')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_stage(self, awsession):
        url = reverse('awsbackup:stage')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_transaction(self, awsession):
        url = reverse('awsbackup:transaction')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_opspeed(self, awsession):
        url = reverse('awsbackup:opspeed')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_stoptime(self, awesesion):
        url = reverse('awsbackup:stoptime')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')

    @mock.patch('awsbackup.views.AWSSession')
    def test_site_activeDownloadLink(self, awsession):
        url = reverse('awsbackup:activeDownloadLink')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')
