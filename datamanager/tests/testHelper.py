# -*- coding: utf-8 -*-
from testhelper.helper import TestHelper
from datamanager.helper import FileManager


class TestFileManager(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.file_manager = FileManager()

    def test__get_file_list(self):
        print(self.file_manager.get_file_list())