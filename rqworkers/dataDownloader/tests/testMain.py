# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from loadData import main

import mock
import os


class Main(TestCase):

    def setUp(self):
        pass

    def set_search_mock(self, search_mock):
        search_mock.return_value = search_mock
        search_mock.execute.return_value = search_mock
        search_mock.__getitem__.return_value = search_mock
        type(search_mock).filter = mock.PropertyMock(return_value=search_mock)
        type(search_mock).hits = mock.PropertyMock(return_value=search_mock)
        type(search_mock).total = mock.PropertyMock(return_value=0)

    def set_argparse_mock(self, argparse_mock, file_path_pattern):
        argparse_mock.return_value = argparse_mock
        argparse_mock.ArgumentParser.return_value = argparse_mock
        argparse_mock.parse_args.return_value = argparse_mock
        type(argparse_mock).file = mock.PropertyMock(return_value=[file_path_pattern])

    @mock.patch('uploader.datafile.parallel_bulk')
    @mock.patch('uploader.datafile.Search')
    @mock.patch('loadData.argparse')
    @mock.patch('loadData.Elasticsearch')
    def test_load_file_data_(self, elasticsearch_mock, argparse_mock, search_mock, parallel_bulk):
        pattern_list = ['*.profile', '*.expedition', '*.general', '*.od', '*.shape', '*.speed',
                        '*.stop', '*.trip', ]
        for pattern in pattern_list:
            file_path_pattern = os.path.join(os.path.dirname(__file__), 'files', pattern)
            self.set_argparse_mock(argparse_mock, file_path_pattern)
            self.set_search_mock(search_mock)

            parallel_bulk.return_value = [(True, 'info')]
            main()

    @mock.patch('uploader.datafile.parallel_bulk')
    @mock.patch('uploader.datafile.Search')
    @mock.patch('loadData.argparse')
    @mock.patch('loadData.Elasticsearch')
    def test_load_zipped_file_data(self, elasticsearch_mock, argparse_mock, search_mock, parallel_bulk):
        # elasticsearch_mock
        pattern_list = ['*.profile.zip', '*.expedition.zip', '*.general.zip', '*.od.zip', '*.shape.zip', '*.speed.zip',
                        '*.stop.zip', '*.trip.zip', ]
        for pattern in pattern_list:
            file_path_pattern = os.path.join(os.path.dirname(__file__), 'files', pattern)

            self.set_argparse_mock(argparse_mock, file_path_pattern)
            self.set_search_mock(search_mock)

            parallel_bulk.return_value = [(True, 'info')]
            main()
