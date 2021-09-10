from unittest import mock

from django.test import TestCase

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.stage import ESStageHelper


class ESStageHelperTest(TestCase):

    def setUp(self):
        self.instance = ESStageHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days(valid_operator_list=[])
        self.assertListEqual(result, [])

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days_between_dates(self, _get_available_days):
        _get_available_days.return_value = ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-05']
        result = self.instance.get_available_days_between_dates('2020-01-01', '2020-01-05', valid_operator_list=[])
        self.assertListEqual(result, ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-05'])

    def test_get_transfers_base_query_without_dates(self):
        dates = []
        day_types = ['LABORAL']
        communes = [0, 1]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist,
                          self.instance.get_transfers_base_query, dates, day_types, communes)

    def test_get_transfers_base_query(self):
        dates = [['2020-01-01', '2020-01-03']]
        day_types = ['LABORAL']
        communes = [0, 1]
        result = self.instance.get_transfers_base_query(dates, day_types, communes)
        expect_result = {'query': {'bool': {'filter': [{'range': {
            'boardingTime': {'gte': '2020-01-01||/d', 'lte': '2020-01-03||/d', 'format': 'yyyy-MM-dd',
                             'time_zone': '+00:00'}}}, {'terms': {'dayType': ['LABORAL']}},
            {'terms': {'boardingStopCommune': [0, 1]}},
            {'range': {'stageNumber': {'gt': 1}}}]}}, 'from': 0, 'size': 0}

        self.assertEqual(result.to_dict(), expect_result)

    def test_get_post_products_aggregated_transfers_data_query(self):
        dates = [['2020-01-01', '2020-01-03']]
        day_types = ['LABORAL']
        communes = [0, 1]
        result = self.instance.get_post_products_aggregated_transfers_data_query(dates, day_types, communes)
        expected_result = {'query': {'bool': {'filter': [{'range': {
            'boardingTime': {'gte': '2020-01-01||/d', 'lte': '2020-01-03||/d', 'format': 'yyyy-MM-dd',
                             'time_zone': '+00:00'}}}, {'terms': {'dayType': ['LABORAL']}},
            {'terms': {'boardingStopCommune': [0, 1]}},
            {'range': {'stageNumber': {'gt': 1}}}]}}, 'aggs': {
            'result': {'date_histogram': {'field': 'boardingTime', 'interval': 'day'}, 'aggs': {
                'dayType': {'terms': {'field': 'dayType', 'size': 4}, 'aggs': {
                    'boardingStopCommune': {'terms': {'field': 'boardingStopCommune', 'size': 48}, 'aggs': {
                        'authStopCode': {'terms': {'field': 'authStopCode', 'size': 13000}, 'aggs': {
                            'halfHourInBoardingTime': {'terms': {'field': 'halfHourInBoardingTime', 'size': 48},
                                                       'aggs': {'expandedBoarding': {
                                                           'avg': {'field': 'expandedBoarding'}}}}}}}}}}}}}, 'from': 0,
            'size': 0}

        self.assertEqual(expected_result, result.to_dict())

    def test_get_post_products_transfers_data_query(self):
        dates = [['2020-01-01', '2020-01-03']]
        day_types = ['LABORAL']
        communes = [0, 1]
        result = self.instance.get_post_products_transfers_data_query(dates, day_types, communes)
        expected_result = {'query': {'bool': {'filter': [{'range': {
            'boardingTime': {'gte': '2020-01-01||/d', 'lte': '2020-01-03||/d', 'format': 'yyyy-MM-dd',
                             'time_zone': '+00:00'}}}, {'terms': {'dayType': ['LABORAL']}},
            {'terms': {'boardingStopCommune': [0, 1]}},
            {'range': {'stageNumber': {'gt': 1}}}]}}, 'aggs': {
            'result': {'terms': {'field': 'dayType', 'size': 4}, 'aggs': {
                'boardingStopCommune': {'terms': {'field': 'boardingStopCommune', 'size': 48}, 'aggs': {
                    'authStopCode': {'terms': {'field': 'authStopCode', 'size': 13000}, 'aggs': {
                        'halfHourInBoardingTime': {'terms': {'field': 'halfHourInBoardingTime', 'size': 48}, 'aggs': {
                            'expandedBoarding': {'avg': {'field': 'expandedBoarding'}}}}}}}}}}}, 'from': 0, 'size': 0}

        self.assertEqual(expected_result, result.to_dict())

    def test_get_post_products_aggregated_transfers_data_by_operator_query(self):
        dates = [['2020-01-01', '2020-01-03']]
        day_types = ['LABORAL']
        result = self.instance.get_post_products_aggregated_transfers_data_by_operator_query(dates, day_types)
        expected_result = {'query': {'bool': {'filter': [{'range': {
            'boardingTime': {'gte': '2020-01-01||/d', 'lte': '2020-01-03||/d', 'format': 'yyyy-MM-dd',
                             'time_zone': '+00:00'}}}, {'terms': {'dayType': ['LABORAL']}},
            {'range': {'stageNumber': {'gt': 1}}}]}}, 'aggs': {
            'result': {'date_histogram': {'field': 'boardingTime', 'interval': 'day'}, 'aggs': {
                'dayType': {'terms': {'field': 'dayType', 'size': 4}, 'aggs': {
                    'timePeriodInBoardingTime': {'terms': {'field': 'timePeriodInBoardingTime', 'size': 100}, 'aggs': {
                        'halfHourInBoardingTime': {'terms': {'field': 'halfHourInBoardingTime', 'size': 48}, 'aggs': {
                            'authStopCode': {'terms': {'field': 'authStopCode', 'size': 13000}, 'aggs': {
                                'operator': {'terms': {'field': 'operator', 'size': 20}, 'aggs': {
                                    'busStation': {'terms': {'field': 'busStation', 'size': 2}, 'aggs': {
                                        'expandedBoarding': {'sum': {'field': 'expandedBoarding'}}}}}}}}}}}}}}}}},
            'from': 0, 'size': 0}
        self.assertEqual(expected_result, result.to_dict())
