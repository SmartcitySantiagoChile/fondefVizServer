from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_map(self):
        self.check_http_response(self.client, 'shape:map', 200)
