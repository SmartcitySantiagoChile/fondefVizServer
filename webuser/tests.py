from django.apps import apps
from django.urls import reverse

from testhelper.helper import TestHelper
from webuser.apps import WebuserConfig


class WebuserConfigTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_apps(self):
        self.assertEqual(WebuserConfig.name, 'webuser')
        self.assertEqual(apps.get_app_config('webuser').name, 'webuser')

    def test_PasswordChangeView(self):
        url = reverse('webuser:password_change')
        response = self.client.get(url)
        self.assertNotContains(response, 'status')
