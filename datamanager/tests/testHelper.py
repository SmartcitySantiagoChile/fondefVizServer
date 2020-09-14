# -*- coding: utf-8 -*-
from testhelper.helper import TestHelper
from datamanager.helper import FileManager
import mock
import datetime

class TestFileManager(TestHelper):
    fixtures = ['loaddata.json']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.file_manager = FileManager()


    def test__get_file_list(self):
        {'stop': [{'name': '2020-01-01.stop', 'discoveredAt': datetime.datetime(2020, 9, 11, 20, 57, 58, 369000,
                                                                                tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2019, 11, 29, 16, 9, 36, tzinfo= < UTC >), 'lines': 917, 'id': 1, 'lastExecution': None}], 'shape': [
            {'name': '2019-10-12.shape', 'discoveredAt': datetime.datetime(2020, 9, 11, 21, 15, 36, 632000,
                                                                           tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 27, 20, 59, 26, 831000,
            tzinfo= < UTC >), 'lines': 1427, 'id': 2, 'lastExecution': None}], 'opdata': [{'name': '2018-03-01.opdata',
                                                                                           'discoveredAt': datetime.datetime(
                                                                                               2020, 9, 11, 21, 16, 12,
                                                                                               567000,
                                                                                               tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 6, 18, 22, 17, 15, 518000, tzinfo= < UTC >), 'lines': 778, 'id': 3, 'lastExecution': None}], 'bip': [
            {'name': '2019-10-08.bip', 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 822000,
                                                                         tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 25, 15, 25, 56, 761000,
            tzinfo= < UTC >), 'lines': 5892312, 'id': 4, 'lastExecution': None}], 'general': [
            {'name': '2019-10-21.general', 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 849000,
                                                                             tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 17, 15, 32, 10, 927000, tzinfo= < UTC >), 'lines': 1, 'id': 5, 'lastExecution': None}], 'trip': [
            {'name': '2019-10-21.trip', 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 38, 901000,
                                                                          tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 26, 14, 8, 24, 904000,
            tzinfo= < UTC >), 'lines': 3091226, 'id': 6, 'lastExecution': None}], 'speed': [{'name': '2019-10-27.speed',
                                                                                             'discoveredAt': datetime.datetime(
                                                                                                 2020, 9, 14, 13, 54,
                                                                                                 38, 921000,
                                                                                                 tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 26, 16, 20, 50, 473000,
            tzinfo= < UTC >), 'lines': 834843, 'id': 7, 'lastExecution': None}], 'profile': [
            {'name': '2019-08-05.profile', 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 54, 39, 339000,
                                                                             tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 5, 12, 17, 11, 15, 74000,
            tzinfo= < UTC >), 'lines': 3747960, 'id': 8, 'lastExecution': None}], 'paymentfactor': [
            {'name': '2019-10-17.paymentfactor', 'discoveredAt': datetime.datetime(2020, 9, 14, 13, 57, 41, 911000,
                                                                                   tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 25, 15, 7, 59, 485000,
            tzinfo= < UTC >), 'lines': 240, 'id': 9, 'lastExecution': None}], 'odbyroute': [
            {'name': '2019-10-17.odbyroute', 'discoveredAt': datetime.datetime(2020, 9, 14, 14, 38, 15, 434000,
                                                                               tzinfo= < UTC >), 'lastModified': datetime.datetime(
            2020, 3, 26, 13, 15, 24, 266000, tzinfo= < UTC >), 'lines': 0, 'id': 10, 'lastExecution': None}]}

        print(dict(self.file_manager._get_file_list()))

    # @mock.patch('esapi.helper.bip.ESBipHelper')
    # @mock.patch('esapi.helper.odbyroute.ESODByRouteHelper')
    # @mock.patch('esapi.helper.opdata.ESOPDataHelper')
    # @mock.patch('esapi.helper.paymentfactor.ESPaymentFactorHelper')
    # @mock.patch('esapi.helper.resume.ESResumeStatisticHelper')
    # @mock.patch('esapi.helper.shape.ESShapeHelper')
    # @mock.patch('esapi.helper.speed.ESSpeedHelper')
    # @mock.patch('esapi.helper.stop.ESStopHelper')
    # @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper')
    # @mock.patch('esapi.helper.trip.ESTripHelper')
    # def test__get_file_list(self, trip, stopbyroute, stop, speed, shape, resume, paymentfactor, opdata, odbyroute, bip):
    #     expected_file_list = {}
    #     print(dict(self.file_manager.get_file_list()))