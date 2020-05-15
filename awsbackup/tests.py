import mock
from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from awsbackup.admin import DownloadLinkAdmin
from awsbackup.apps import AwsbackupConfig
from awsbackup.models import DownloadLink
from testhelper.helper import TestHelper


class AwsbackupConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AwsbackupConfig.name, 'awsbackup')
        self.assertEqual(apps.get_app_config('awsbackup').name, 'awsbackup')


class AdminTest(TestCase):
    def test_DownloadLinkAdmin(self):
        my_model_admin = DownloadLinkAdmin(model=DownloadLink, admin_site=AdminSite())
        super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                   password='pass')
        # filename = "filename"
        # created_at = mock.MagicMock
        # expire_at = mock.MagicMock
        # url = mock.MagicMock
        # my_model_admin.save_model(obj=DownloadLink(), request=mock.MagicMock(user=super_user), form=None, change=None)
        # self.assertTrue(True)


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
