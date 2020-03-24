# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.test import TestCase

from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryOperationProgramDoesNotExist, \
    ESQueryShapeDoesNotExist, ESQueryThereIsMoreThanOneOperationProgram, \
    ESQueryDateRangeParametersDoesNotExist
from esapi.helper.shape import ESShapeHelper


class ESShapeIndexTest(TestCase):

    def setUp(self):
        self.instance = ESShapeHelper()

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
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

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
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

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
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

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
    def test_get_most_recent_operation_program_date_without_dates(self, get_base_query):
        asked_date = '2018-01-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.get_unique_list_query.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).unique = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[])
        self.assertRaises(ESQueryOperationProgramDoesNotExist, self.instance.get_most_recent_operation_program_date,
                          asked_date)

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
    def test_get_most_recent_operation_program_date(self, get_base_query):
        asked_date = '2018-01-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.get_unique_list_query.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).unique = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[get_base_query])
        type(get_base_query).key_as_string = mock.PropertyMock(return_value=['key'])
        result = self.instance.get_most_recent_operation_program_date(asked_date)
        self.assertListEqual(result, ['key'])

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
    def test_get_route_shape(self, get_base_query):
        auth_route_code = ''
        dates = [[]]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_route_shape, auth_route_code, dates)
        dates = [["2018-01-01"]]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_route_shape, auth_route_code, dates)
        auth_route_code = 'auth_route_code'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.query.return_value = get_base_query
        get_base_query.sort.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        hit = mock.Mock()
        type(get_base_query).hits = mock.PropertyMock(return_value=hit)
        type(hit).hits = mock.PropertyMock(return_value=[{'_source': [1, 2, 3]}])
        result = self.instance.get_route_shape(auth_route_code, dates)
        self.assertListEqual(result, [1, 2, 3])

    @mock.patch('esapi.helper.shape.ESShapeHelper.get_base_query')
    def test_get_route_shape_out_of_index(self, get_base_query):
        auth_route_code = 'auth_route_code'
        dates = [["2018-01-01"]]
        get_base_query.return_value = get_base_query
        get_base_query.query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.sort.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        hit = mock.Mock()
        type(hit).hits = mock.PropertyMock(return_value=[])
        type(get_base_query).hits = mock.PropertyMock(return_value=hit)
        self.assertRaises(ESQueryShapeDoesNotExist, self.instance.get_route_shape, auth_route_code, dates)

    @mock.patch('esapi.helper.shape.ESShapeHelper.make_multisearch_query_for_aggs')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_attr_list')
    def test_get_route_list(self, get_attr_list, make_multisearch_query_for_aggs):
        get_attr_list.return_value = list()
        make_multisearch_query_for_aggs.return_value = dict()
        result = self.instance.get_route_list()
        self.assertIsInstance(result, list)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])
