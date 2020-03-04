# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
import mock
from elasticsearch_dsl import Search
from esapi.helper.resume import ESResumeStatisticHelper


class ESResumeIndexTest(TestCase):

    def setUp(self):
        self.instance = ESResumeStatisticHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])

    def test_get_data(self):
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        metrics = []
        expected = {'query': {'bool': {'filter': [{'range': {
            'date': {'time_zone': '+00:00', 'gte': u'2018-01-01||/d', 'lte': u'2018-02-01||/d',
                     'format': 'yyyy-MM-dd'}}}]}},
                    '_source': ['date', 'transactionWithoutRoute', 'transactionWithRoute', 'transactionNumber',
                                'transactionOnTrainNumber', 'transactionOnMetroNumber', 'transactionOnBusNumber',
                                'transactionOnBusStation', 'averageVelocityInAfternoonRushTrips',
                                'averageTimeInAfternoonRushTrips', 'averageDistanceInAfternoonRushTrips',
                                'tripNumberInAfternoonRushHour', 'averageVelocityInMorningRushTrips',
                                'averageTimeInMorningRushTrips', 'averageDistanceInMorningRushTrips',
                                'tripNumberInMorningRushHour', 'licensePlateNumber', 'GPSPointsNumber',
                                'GPSNumberWithRoute', 'GPSNumberWithoutRoute', 'expeditionNumber', 'maxExpeditionTime',
                                'minExpeditionTime', 'averageExpeditionTime', 'smartcardNumber', 'tripNumber',
                                'averageTimeOfTrips', 'averageVelocityOfTrips', 'averageTimeBetweenGPSPoints',
                                'averageDistanceOfTrips', 'tripsThatUseMetro', 'completeTripNumber',
                                'stagesWithBusStationAlighting', 'tripsWithoutLastAlighting', 'validTripNumber',
                                'tripsWithOneStage', 'tripsWithTwoStages', 'tripsWithThreeStages',
                                'tripsWithFourStages', 'tripsWithFiveOrMoreStages', 'tripsWithOnlyMetro',
                                'stagesWithBusAlighting', 'stagesWithTrainAlighting', 'stagesWithMetroAlighting',
                                'dayType', 'version', 'transactionInMorningRushHour', 'transactionInAfternoonRushHour',
                                'alightingNumber', 'alightingNumberInMorningRushHour',
                                'alightingNumberInAfternoonRushHour', 'stopsNumberWithTypeE', 'stopsNumberWithTypeT',
                                'stopsNumberWithTypeL', 'stopsNumberWithTypeI', 'transactionNumberInStopsWithTypeE',
                                'transactionNumberInStopsWithTypeT', 'transactionNumberInStopsWithTypeL',
                                'transactionNumberInStopsWithTypeI', 'firstStopWithMoreValidations',
                                'secondStopWithMoreValidations', 'thirdStopWithMoreValidations',
                                'fourthStopWithMoreValidations', 'fifthStopWithMoreValidations',
                                'sixthStopWithMoreValidations', 'seventhStopWithMoreValidations',
                                'eighthStopWithMoreValidations', 'ninethStopWithMoreValidations',
                                'tenthStopWithMoreValidations', 'transactionNumberInFirstStopWithMoreValidations',
                                'transactionNumberInSecondStopWithMoreValidations',
                                'transactionNumberInThirdStopWithMoreValidations',
                                'transactionNumberInFourthStopWithMoreValidations',
                                'transactionNumberInFifthStopWithMoreValidations',
                                'transactionNumberInSixthStopWithMoreValidations',
                                'transactionNumberInSeventhStopWithMoreValidations',
                                'transactionNumberInEighthStopWithMoreValidations',
                                'transactionNumberInNinethStopWithMoreValidations',
                                'transactionNumberInTenthStopWithMoreValidations', 'firstBusStopWithMoreValidations',
                                'secondBusStopWithMoreValidations', 'thirdBusStopWithMoreValidations',
                                'fourthBusStopWithMoreValidations', 'fifthBusStopWithMoreValidations',
                                'sixthBusStopWithMoreValidations', 'seventhBusStopWithMoreValidations',
                                'eighthBusStopWithMoreValidations', 'ninethBusStopWithMoreValidations',
                                'tenthBusStopWithMoreValidations', 'transactionNumberInFirstBusStopWithMoreValidations',
                                'transactionNumberInSecondBusStopWithMoreValidations',
                                'transactionNumberInThirdBusStopWithMoreValidations',
                                'transactionNumberInFourthBusStopWithMoreValidations',
                                'transactionNumberInFifthBusStopWithMoreValidations',
                                'transactionNumberInSixthBusStopWithMoreValidations',
                                'transactionNumberInSeventhBusStopWithMoreValidations',
                                'transactionNumberInEighthBusStopWithMoreValidations',
                                'transactionNumberInNinethBusStopWithMoreValidations',
                                'transactionNumberInTenthBusStopWithMoreValidations']}

        result = self.instance.get_data(start_date, end_date, metrics)
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)
