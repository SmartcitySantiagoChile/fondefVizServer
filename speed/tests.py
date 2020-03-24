from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_matrix(self):
        self.check_http_response(self.client, 'speed:matrix', 200)

    def test_site_ranking(self):
        self.check_http_response(self.client, 'speed:ranking', 200)

    def test_site_variation(self):
        self.check_http_response(self.client, 'speed:variation', 200)
