# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

import mock

from esapi.helper.stop import ESStopHelper
from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryStopInfoDoesNotExist, \
    ESQueryDateParametersDoesNotExist, ESQueryResultEmpty


class ESStopIndexTest(TestCase):

    def setUp(self):
        self.instance = ESStopHelper()

    @mock.patch('esapi.helper.stop.ESStopHelper.make_multisearch_query_for_aggs')
    def test_get_matched_stop_list(self, make_multisearch_query_for_aggs):
        es_query = mock.Mock()
        ans = mock.Mock()
        type(es_query).aggregations = mock.PropertyMock(return_value=es_query)
        type(es_query).unique = mock.PropertyMock(return_value=es_query)
        type(ans).key = mock.PropertyMock(return_value='key')
        type(ans).additional_info = mock.PropertyMock(return_value=ans)
        type(ans).hits = mock.PropertyMock(return_value=[ans])
        type(ans).authCode = mock.PropertyMock(return_value='auth_code')
        type(es_query).buckets = mock.PropertyMock(return_value=[ans])
        make_multisearch_query_for_aggs.return_value = [es_query]
        result = self.instance.get_matched_stop_list('term')
        self.assertListEqual(result, [('key', 'auth_code')])

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_stop_info(self, get_base_query):
        auth_stop_code = ''
        start_date = '[[""]]'
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_stop_info, start_date, auth_stop_code)
        auth_stop_code = 'auth_stop_code'
        start_date = '[["2018-01-01"]]'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.sort.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        hit = mock.Mock()
        type(get_base_query).hits = mock.PropertyMock(return_value=hit)
        type(hit).hits = mock.PropertyMock(return_value=[{
            '_source': {
                'path': 1,
                'timestamp': 2,
                'key': 'value'
            }
        }])
        result = self.instance.get_stop_info(start_date, auth_stop_code)
        self.assertDictEqual(result, {'key': 'value'})

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_stop_info_with_empty_stop_info(self, get_base_query):
        auth_stop_code = 'auth_stop_code'
        start_date = '2018-01-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.sort.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        hit = mock.Mock()
        type(get_base_query).hits = mock.PropertyMock(return_value=hit)
        type(hit).hits = mock.PropertyMock(return_value=[])
        self.assertRaises(ESQueryStopInfoDoesNotExist, self.instance.get_stop_info, start_date, auth_stop_code)
