from unittest import mock

from django.test import TestCase

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.paymentfactor import ESPaymentFactorHelper


class ESPaymentFactorIndexTest(TestCase):

    def setUp(self):
        self.instance = ESPaymentFactorHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])

    def test_get_data(self):
        dates = []
        day_type = ["day_type"]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_data,
                          dates, day_type)
        dates = [['2018-01-01']]
        expected = {'query': {'bool': {'filter': [{'terms': {'dayType': ['day_type']}}, {'range': {
            'date': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-01-01||/d',
                     'format': 'yyyy-MM-dd'}}}]}}, 'from': 0, 'aggs': {
            'by_bus_station_id': {'terms': {'field': 'busStationId', 'size': 10000}, 'aggs': {
                'by_bus_station_name': {'terms': {'field': 'busStationName'}, 'aggs': {
                    'by_assignation': {'terms': {'field': 'assignation'}, 'aggs': {
                        'by_operator': {'terms': {'field': 'operator'}, 'aggs': {
                            'by_day_type': {'terms': {'field': 'dayType'}, 'aggs': {
                                'by_date': {'terms': {'field': 'date', 'size': 10000},
                                            'aggs': {'factor': {'sum': {'field': 'factor'}}}},
                                'sum': {'sum': {'field': 'sum'}}, 'total': {'sum': {'field': 'total'}},
                                'neutral': {'sum': {'field': 'neutral'}},
                                'subtraction': {'sum': {'field': 'subtraction'}}}}}}}}}}}}}, 'size': 0}

        result = self.instance.get_data(dates, day_type)
        self.assertDictEqual(expected, result.to_dict())
