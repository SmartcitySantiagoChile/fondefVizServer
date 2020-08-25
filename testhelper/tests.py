# -*- coding: utf-8 -*-

from testhelper.helper import TestHelper


class AdminTests(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.data = {
        }

    def test_admin_auth_user_changelist(self):
        self.check_http_response(self.client, 'admin:auth_user_changelist', 200)

    def test_admin_localinfo_operator_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_operator_changelist', 200)

    def test_admin_localinfo_halfhour_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_halfhour_changelist', 200)

    def test_admin_datamanager_datasourcepath_changelist(self):
        self.check_http_response(self.client, 'admin:datamanager_datasourcepath_changelist', 200)

    def test_admin_localinfo_opdictionary_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_opdictionary_changelist', 200)

    def test_admin_datamanager_uploaderjobexecution_changelist(self):
        self.check_http_response(self.client, 'admin:datamanager_uploaderjobexecution_changelist', 200)

    def test_admin_datamanager_exporterjobexecution_changelist(self):
        self.check_http_response(self.client, 'admin:datamanager_exporterjobexecution_changelist', 200)

    def test_admin_awsbackup_downloadlink_changelist(self):
        self.check_http_response(self.client, 'admin:awsbackup_downloadlink_changelist', 200)

    def test_admin_logapp_usersession_changelist(self):
        self.check_http_response(self.client, 'admin:logapp_usersession_changelist', 200)

    def test_admin_logapp_usersessionstats_changelist(self):
        self.check_http_response(self.client, 'admin:logapp_usersessionstats_changelist', 200)

    def test_admin_localinfo_daydescription_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_daydescription_changelist', 200)

    def test_admin_localinfo_calendarinfo_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_calendarinfo_changelist', 200)

    def test_admin_localinfo_faq_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_faq_changelist', 200)
