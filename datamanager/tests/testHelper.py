# -*- coding: utf-8 -*-
import datetime
from unittest import mock

import pytz

from datamanager.helper import FileManager
from testhelper.helper import TestHelper


class TestFileManager(TestHelper):
    fixtures = ['loaddata.json']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.file_manager = FileManager()

    def test__get_file_list(self):
        expected = {
            'stop': [
                {'name': '2020-01-01.stop',
                 'discoveredAt': datetime.datetime(2020, 9, 11, 20, 57, 58, 369000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2019, 11, 29, 16, 9, 36, tzinfo=pytz.utc), 'lines': 917, 'id': 1, 'lastExecution': None}],
            'shape': [
                {'name': '2019-10-12.shape',
                 'discoveredAt': datetime.datetime(2020, 9, 11, 21, 15, 36, 632000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 27, 20, 59, 26, 831000, tzinfo=pytz.utc), 'lines': 1427, 'id': 2, 'lastExecution': None}],
            'opdata': [
                {'name': '2018-03-01.opdata',
                 'discoveredAt': datetime.datetime(
                     2020, 9, 11, 21, 16, 12,
                     567000, tzinfo=pytz.utc), 'lastModified': datetime.datetime(
                    2020, 6, 18, 22, 17, 15, 518000, tzinfo=pytz.utc), 'lines': 778, 'id': 3, 'lastExecution': None}],
            'bip': [
                {'name': '2019-10-08.bip',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 822000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 25, 15, 25, 56, 761000, tzinfo=pytz.utc), 'lines': 5892312, 'id': 4,
                 'lastExecution': None}],
            'general': [
                {'name': '2019-10-21.general',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 849000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 17, 15, 32, 10, 927000, tzinfo=pytz.utc), 'lines': 1, 'id': 5, 'lastExecution': None}],
            'trip': [
                {'name': '2019-10-21.trip',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 901000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 26, 14, 8, 24, 904000, tzinfo=pytz.utc), 'lines': 3091226, 'id': 6,
                 'lastExecution': None}],
            'speed': [
                {'name': '2019-10-27.speed',
                 'discoveredAt': datetime.datetime(
                     2020, 9, 14, 13, 54,
                     38, 921000, tzinfo=pytz.utc), 'lastModified': datetime.datetime(
                    2020, 3, 26, 16, 20, 50, 473000, tzinfo=pytz.utc), 'lines': 834843, 'id': 7,
                 'lastExecution': None}],
            'profile': [
                {'name': '2019-08-05.profile',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 39, 339000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 5, 12, 17, 11, 15, 74000, tzinfo=pytz.utc), 'lines': 3747960, 'id': 8,
                 'lastExecution': None}],
            'paymentfactor': [
                {'name': '2019-10-17.paymentfactor',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 57, 41, 911000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 25, 15, 7, 59, 485000, tzinfo=pytz.utc), 'lines': 240, 'id': 9, 'lastExecution': None}],
            'odbyroute': [
                {'name': '2019-10-17.odbyroute',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 14, 38, 15, 434000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 26, 13, 15, 24, 266000, tzinfo=pytz.utc), 'lines': 0, 'id': 10, 'lastExecution': None}]}

        self.assertEqual(expected, self.file_manager._get_file_list())

        filter_bip_expected = {'bip': [
            {'name': '2019-10-08.bip',
             'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 822000, tzinfo=pytz.utc),
             'lastModified': datetime.datetime(
                 2020, 3, 25, 15, 25, 56, 761000, tzinfo=pytz.utc), 'lines': 5892312, 'id': 4, 'lastExecution': None}]}
        self.assertEqual(filter_bip_expected, self.file_manager._get_file_list(index_filter=['bip']))

    @mock.patch('datamanager.helper.ESBipHelper')
    @mock.patch('datamanager.helper.ESODByRouteHelper')
    @mock.patch('datamanager.helper.ESOPDataHelper')
    @mock.patch('datamanager.helper.ESPaymentFactorHelper')
    @mock.patch('datamanager.helper.ESResumeStatisticHelper')
    @mock.patch('datamanager.helper.ESShapeHelper')
    @mock.patch('datamanager.helper.ESSpeedHelper')
    @mock.patch('datamanager.helper.ESStopHelper')
    @mock.patch('datamanager.helper.ESStopByRouteHelper')
    @mock.patch('datamanager.helper.ESTripHelper')
    @mock.patch('datamanager.helper.ESProfileHelper')
    def test_get_document_number_by_file_from_elasticsearch(self, profile, trip, stopbyroute, stop, speed, shape,
                                                            resume,
                                                            paymentfactor, opdata, odbyroute, bip):
        expected = {'key': 1}
        buckets = [mock.MagicMock(key='key', doc_count=1)]
        files = mock.MagicMock(buckets=buckets)
        aggregations = mock.MagicMock(files=files)
        execute = mock.MagicMock(aggregations=aggregations)
        data_by_file = mock.MagicMock(execute=mock.MagicMock(return_value=execute))
        profile.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        trip.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        stopbyroute.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        stop.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        speed.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        shape.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        resume.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        paymentfactor.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        opdata.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        odbyroute.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        bip.return_value = mock.MagicMock(get_data_by_file=mock.MagicMock(return_value=data_by_file))
        self.assertEqual(expected, self.file_manager.get_document_number_by_file_from_elasticsearch())
        self.assertEqual(expected,
                         self.file_manager.get_document_number_by_file_from_elasticsearch(index_filter=['stop']))
        self.assertEqual(expected, self.file_manager.get_document_number_by_file_from_elasticsearch(
            file_filter='2020-01-01.stop'))
        self.assertEqual(expected, self.file_manager.get_document_number_by_file_from_elasticsearch(
            file_filter=['2020-01-01.stop', '2020-01-02.stop']))

    @mock.patch("datamanager.helper.FileManager.get_document_number_by_file_from_elasticsearch")
    def test_get_file_list(self, get_document_es):
        expected = {
            'stop': [
                {'name': '2020-01-01.stop',
                 'discoveredAt': datetime.datetime(2020, 9, 11, 20, 57, 58, 369000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2019, 11, 29, 16, 9, 36, tzinfo=pytz.utc), 'lines': 917, 'id': 1, 'lastExecution': None,
                 'docNumber': 0}],
            'shape': [
                {'name': '2019-10-12.shape',
                 'discoveredAt': datetime.datetime(2020, 9, 11, 21, 15, 36, 632000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 27, 20, 59, 26, 831000, tzinfo=pytz.utc), 'lines': 1427, 'id': 2, 'lastExecution': None,
                 'docNumber': 0}],
            'opdata': [
                {'name': '2018-03-01.opdata',
                 'discoveredAt': datetime.datetime(
                     2020, 9, 11, 21, 16, 12,
                     567000, tzinfo=pytz.utc), 'lastModified': datetime.datetime(
                    2020, 6, 18, 22, 17, 15, 518000, tzinfo=pytz.utc), 'lines': 778, 'id': 3, 'lastExecution': None,
                 'docNumber': 0}],
            'bip': [
                {'name': '2019-10-08.bip',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 822000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 25, 15, 25, 56, 761000, tzinfo=pytz.utc), 'lines': 5892312, 'id': 4,
                 'lastExecution': None, 'docNumber': 0}],
            'general': [
                {'name': '2019-10-21.general',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 849000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 17, 15, 32, 10, 927000, tzinfo=pytz.utc), 'lines': 1, 'id': 5, 'lastExecution': None,
                 'docNumber': 0}],
            'trip': [
                {'name': '2019-10-21.trip',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 901000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 26, 14, 8, 24, 904000, tzinfo=pytz.utc), 'lines': 3091226, 'id': 6,
                 'lastExecution': None, 'docNumber': 0}],
            'speed': [
                {'name': '2019-10-27.speed',
                 'discoveredAt': datetime.datetime(
                     2020, 9, 14, 13, 54,
                     38, 921000, tzinfo=pytz.utc), 'lastModified': datetime.datetime(
                    2020, 3, 26, 16, 20, 50, 473000, tzinfo=pytz.utc), 'lines': 834843, 'id': 7,
                 'lastExecution': None, 'docNumber': 0}],
            'profile': [
                {'name': '2019-08-05.profile',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 39, 339000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 5, 12, 17, 11, 15, 74000, tzinfo=pytz.utc), 'lines': 3747960, 'id': 8,
                 'lastExecution': None, 'docNumber': 0}],
            'paymentfactor': [
                {'name': '2019-10-17.paymentfactor',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 57, 41, 911000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 25, 15, 7, 59, 485000, tzinfo=pytz.utc), 'lines': 240, 'id': 9, 'lastExecution': None,
                 'docNumber': 0}],
            'odbyroute': [
                {'name': '2019-10-17.odbyroute',
                 'discoveredAt': datetime.datetime(2020, 9, 14, 14, 38, 15, 434000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2020, 3, 26, 13, 15, 24, 266000, tzinfo=pytz.utc), 'lines': 0, 'id': 10, 'lastExecution': None,
                 'docNumber': 0}]}
        self.assertEqual(expected, self.file_manager.get_file_list())

        stop_expected = {
            'stop': [
                {'name': '2020-01-01.stop',
                 'discoveredAt': datetime.datetime(2020, 9, 11, 20, 57, 58, 369000, tzinfo=pytz.utc),
                 'lastModified': datetime.datetime(
                     2019, 11, 29, 16, 9, 36, tzinfo=pytz.utc), 'lines': 917, 'id': 1, 'lastExecution': None,
                 'docNumber': 0}
            ]
        }
        self.assertEqual(stop_expected, self.file_manager.get_file_list(index_filter=['stop']))

    @mock.patch('datamanager.helper.ESODByRouteHelper')
    @mock.patch('datamanager.helper.ESTripHelper')
    @mock.patch('datamanager.helper.ESProfileHelper')
    def test_get_time_period_list_by_file_from_elasticsearch(self, profile, trip, odbyroute):
        expected = {"01-01-2020":
                        {"profile": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}
                    }
        file_list = [{
            "key": "01-01-2020.profile",
            "time_periods_0": {
                "buckets":
                    [{"key": 1}, {"key": 2}, {"key": 3}, {"key": 4}, {"key": 5}, {"key": 6}, {"key": 7}]
            },
            "time_periods_1": {
                "buckets":
                    [{"key": 1}, {"key": 2}, {"key": 3}, {"key": 11}, {"key": 10}, {"key": 9}, {"key": 8}]
            },
            "dead_key": {}
        }]
        to_dict = {"time_periods_per_file": {"buckets": file_list}}
        aggregations = mock.MagicMock(to_dict=mock.MagicMock(return_value=to_dict))
        execute = mock.MagicMock(aggregations=aggregations)
        get_all_time_periods = mock.MagicMock(execute=mock.MagicMock(return_value=execute))
        profile.return_value = mock.MagicMock(get_all_time_periods=mock.MagicMock(return_value=get_all_time_periods))
        trip.return_value = mock.MagicMock(get_all_time_periods=mock.MagicMock(return_value=get_all_time_periods))
        odbyroute.return_value = mock.MagicMock(get_all_time_periods=mock.MagicMock(return_value=get_all_time_periods))
        self.assertEqual(expected, self.file_manager.get_time_period_list_by_file_from_elasticsearch())
