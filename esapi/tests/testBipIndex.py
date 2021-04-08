# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import mock
from django.test import TestCase

from esapi.errors import ESQueryDateRangeParametersDoesNotExist, ESQueryOperatorParameterDoesNotExist
from esapi.helper.bip import ESBipHelper


class ESBipIndexTest(TestCase):

    def setUp(self):
        self.instance = ESBipHelper()

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])

    def test_get_bip_by_operator_data(self):
        dates = []
        valid_operator_list = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_bip_by_operator_data,
                          dates, valid_operator_list)
        dates = [['2018-01-01']]
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_bip_by_operator_data,
                          dates, valid_operator_list)
        valid_operator_list = [0]
        expected = {'query': {'bool': {'filter': [{'terms': {'operator': [0]}}, {'range': {
            'validationTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-01||/d',
                               u'format': u'yyyy-MM-dd'}}}]}}, 'aggs': {
            u'histogram': {'date_histogram': {'field': u'validationTime', 'interval': u'day'},
                           'aggs': {u'operators': {'terms': {'field': u'operator', 'size': 1000}}}}}}

        result = self.instance.get_bip_by_operator_data(dates, valid_operator_list)
        self.assertDictEqual(result[0].to_dict(), expected)
