# -*- coding: utf-8 -*-


from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_operator(self):
        self.check_http_response(self.client, 'consistencychecker:concistency', 200)

    def test_data_request(self):
        self.check_http_response(self.client, 'consistencychecker:getConsistencyData', 200)
