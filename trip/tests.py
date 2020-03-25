from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_from_to_map(self):
        self.check_http_response(self.client, 'trip:from-to', 200)

    def test_site_large_trips(self):
        self.check_http_response(self.client, 'trip:large-trips', 200)

    def test_site_map(self):
        self.check_http_response(self.client, 'trip:map', 200)

    def test_site_strategies(self):
        self.check_http_response(self.client, 'trip:strategies', 200)

    def test_site_resume(self):
        self.check_http_response(self.client, 'trip:graphs', 200)