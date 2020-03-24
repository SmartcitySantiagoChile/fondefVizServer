# -*- coding: utf-8 -*-


# Create your tests here.
from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_operator(self):
        self.check_http_response(self.client, 'bip:operator', 200)
