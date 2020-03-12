# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your tests here.
from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_operator(self):
        self.check_http_response(self.client, 'paymentfactor:index', 200)
