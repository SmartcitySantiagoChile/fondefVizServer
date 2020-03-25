from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_expedition(self):
        self.check_http_response(self.client, 'profile:expedition', 200)

    def test_site_stop(self):
        self.check_http_response(self.client, 'profile:stop', 200)

    def test_site_trajectory(self):
        self.check_http_response(self.client, 'profile:trajectory', 200)

    def test_site_transfers(self):
        self.check_http_response(self.client, 'profile:transfers', 200)

    def test_site_odmatrix(self):
        self.check_http_response(self.client, 'profile:odmatrix', 200)

    def test_site_manystops(self):
        self.check_http_response(self.client, 'profile:manystops', 200)
