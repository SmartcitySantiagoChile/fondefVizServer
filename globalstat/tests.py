from testhelper.helper import TestHelper


class ConnectionTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()

    def test_site_resume(self):
        self.check_http_response(self.client, 'globalstat:resume', 200)

    def test_site_detail(self):
        self.check_http_response(self.client, 'globalstat:detail', 200)

