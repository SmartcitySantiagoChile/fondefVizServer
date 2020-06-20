# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.test import TestCase

from esapi.errors import ESQueryOperationProgramDoesNotExist, \
    ESQueryThereIsMoreThanOneOperationProgram
from esapi.helper.opdata import ESOPDataHelper


class ESOpDataIndexTest(TestCase):

    def setUp(self):
        self.instance = ESOPDataHelper()

    @mock.patch('esapi.helper.opdata.ESOPDataHelper.get_base_query')
    def test_check_operation_program_between_dates_with_zero_days(self, get_base_query):
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.get_unique_list_query.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).unique = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[])
        self.assertRaises(ESQueryOperationProgramDoesNotExist, self.instance.check_operation_program_between_dates,
                          start_date, end_date)

    @mock.patch('esapi.helper.opdata.ESOPDataHelper.get_base_query')
    def test_check_operation_program_between_dates_with_different_days(self, get_base_query):
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.get_unique_list_query.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        x = mock.Mock()
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).unique = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[x])
        type(x).key_as_string = mock.PropertyMock(return_value='2018-02-01')
        self.assertRaises(ESQueryThereIsMoreThanOneOperationProgram,
                          self.instance.check_operation_program_between_dates,
                          start_date, end_date)

    @mock.patch('esapi.helper.opdata.ESOPDataHelper.get_base_query')
    def test_check_operation_program_between_dates_with_two_days(self, get_base_query):
        start_date = '2018-01-01'
        end_date = '2018-02-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.get_unique_list_query.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        x = mock.Mock()
        y = mock.Mock()
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).unique = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[x, y])
        type(x).key_as_string = mock.PropertyMock(return_value='2018-02-01')
        type(y).key_as_string = mock.PropertyMock(return_value='2018-03-01')
        self.assertRaises(ESQueryThereIsMoreThanOneOperationProgram,
                          self.instance.check_operation_program_between_dates,
                          start_date, end_date)
