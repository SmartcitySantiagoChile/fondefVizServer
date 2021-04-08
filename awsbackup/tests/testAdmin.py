import datetime

from unittest import mock
from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase

from awsbackup.admin import DownloadLinkAdmin
from awsbackup.apps import AwsbackupConfig
from awsbackup.models import DownloadLink


class AwsbackupConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AwsbackupConfig.name, 'awsbackup')
        self.assertEqual(apps.get_app_config('awsbackup').name, 'awsbackup')


class AdminTest(TestCase):

    def setUp(self):
        self.my_model_admin = DownloadLinkAdmin(model=DownloadLink, admin_site=AdminSite())
        super_user = User.objects.create_superuser(username='super', email='super@email.org',
                                                   password='pass')
        filename = "filename"
        created_at = datetime.datetime(2018, 5, 21, tzinfo=datetime.timezone.utc)
        expire_at = datetime.datetime(2018, 6, 21, tzinfo=datetime.timezone.utc)
        url = ''
        self.download_link = DownloadLink(filename=filename, created_at=created_at, expire_at=expire_at, url=url,
                                          user=super_user)
        self.my_model_admin.save_model(
            obj=self.download_link,
            request=mock.MagicMock(user=super_user), form=None, change=None)

    def test_is_active(self):
        self.assertFalse(self.my_model_admin.is_active(self.download_link))

    def test_link(self):
        expected_url = "<a href='' class='btn btn-success btn-xs'><i class='fa fa-file'></i> Descargar</a>"
        expected_not_url = 'link was not created'
        object_without_url = mock.MagicMock(url=None)
        self.assertEqual(expected_url, self.my_model_admin.link(self.download_link))
        self.assertEqual(expected_not_url, self.my_model_admin.link(object_without_url))

    def test_has_add_permission(self):
        self.assertFalse(self.my_model_admin.has_add_permission(mock.MagicMock()))

    def test_get_readonly_fields(self):
        self.assertEqual(('filename', 'url', 'crated_at', 'expire_at'),
                         self.my_model_admin.get_readonly_fields(mock.MagicMock()))
