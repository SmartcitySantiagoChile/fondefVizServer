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
        expected = {'query': {'bool': {'filter': [{'terms': {'dayType': [u'day_type']}}, {'range': {
            'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-01||/d',
                     u'format': u'yyyy-MM-dd'}}}]}}, 'from': 0, 'aggs': {
            u'by_bus_station_id': {'terms': {'field': u'busStationId', 'size': 10000}, 'aggs': {
                u'by_bus_station_name': {'terms': {'field': u'busStationName'}, 'aggs': {
                    u'by_assignation': {'terms': {'field': u'assignation'}, 'aggs': {
                        u'by_operator': {'terms': {'field': u'operator'}, 'aggs': {
                            u'by_day_type': {'terms': {'field': u'dayType'}, 'aggs': {
                                u'by_date': {'terms': {'field': u'date', 'size': 10000},
                                             'aggs': {u'factor': {'sum': {'field': u'factor'}}}},
                                u'sum': {'sum': {'field': u'sum'}}, u'total': {'sum': {'field': u'total'}},
                                u'neutral': {'sum': {'field': u'neutral'}},
                                u'subtraction': {'sum': {'field': u'subtraction'}}}}}}}}}}}}}, 'size': 0}

        result = self.instance.get_data(dates, day_type)
        self.assertDictEqual(expected, result.to_dict())
