from unittest import TestCase

from dataDownloader.csvhelper import helper


class TestBipCSVHelper(TestCase):

    def setUp(self):
        csv_helper = helper.CSVHelper()
