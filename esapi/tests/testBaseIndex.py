# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.test import TestCase, override_settings
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch_dsl import Search

from esapi.helper.basehelper import ElasticSearchHelper


class IndexNameTest(TestCase):

    @mock.patch('esapi.helper.basehelper.settings')
    def test_wrong_index_name(self, settings):
        settings.ES_CLIENT.return_value = None
        fail_name = None
        file_extensions = ['a', 'b']
        self.assertRaises(ValueError, ElasticSearchHelper, fail_name, file_extensions)
        other_fail_name = ''
        self.assertRaises(ValueError, ElasticSearchHelper, other_fail_name, file_extensions)

    @mock.patch('esapi.helper.basehelper.settings')
    def test_good_index_name(self, settings):
        settings.ES_CLIENT.return_value = None
        name = 'goodIndexName'
        file_extensions = []
        self.assertIsInstance(ElasticSearchHelper(name, file_extensions), ElasticSearchHelper)

    @mock.patch('esapi.helper.basehelper.settings')
    def test_index_name(self, settings):
        settings.ES_CLIENT.return_value = None
        name = 'index'
        file_extensions = []
        self.assertEqual(ElasticSearchHelper('index', file_extensions).index_name, name)

    @mock.patch('esapi.helper.basehelper.settings')
    def test_file_extensions(self, settings):
        settings.ES_CLIENT.return_value = None
        name = 'name'
        files = ['file1']
        self.assertListEqual(ElasticSearchHelper(name, files).file_extensions, files)


@override_settings(ES_CLIENT=mock.MagicMock())
class BaseIndexTest(TestCase):

    def setUp(self):
        self.name = 'goodIndexName'
        file_extensions = ['a', 'b']
        self.instance = ElasticSearchHelper(self.name, file_extensions)

    def test_get_base_query(self):
        result = self.instance.get_base_query()
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), {})

    @mock.patch('esapi.helper.basehelper.Search')
    def test_get_attr_list(self, search):
        tag = mock.Mock()
        type(tag).doc_count = 0
        type(search).aggregations = mock.PropertyMock(return_value={'aggs_name': search})
        type(search).buckets = mock.PropertyMock(return_value=[tag])
        result = self.instance.get_attr_list(search, 'aggs_name')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @mock.patch('esapi.helper.basehelper.Search')
    def test_get_attr_list_with_key_as_string(self, search):
        tag = mock.MagicMock()
        tag.__contains__.return_value = dict(key_as_string='value').__contains__
        type(tag).key_as_string = mock.PropertyMock(return_value='value')
        type(search).aggregations = mock.PropertyMock(return_value={'aggs_name': search})
        type(search).buckets = mock.PropertyMock(return_value=[tag])
        result = self.instance.get_attr_list(search, 'aggs_name')
        self.assertListEqual(result, ['value'])

    @mock.patch('esapi.helper.basehelper.Search')
    def test_get_attr_list_with_key(self, search):
        tag = mock.MagicMock()
        tag.__contains__.return_value = False
        type(tag).key = mock.PropertyMock(return_value='value')
        type(search).aggregations = mock.PropertyMock(return_value={'aggs_name': search})
        type(search).buckets = mock.PropertyMock(return_value=[tag])
        result = self.instance.get_attr_list(search, 'aggs_name')
        self.assertListEqual(result, ['value'])

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_multisearch_query_for_aggs(self, multi_search):
        multi_search_instance = multi_search.return_value
        multi_search_instance.add.return_value = multi_search_instance
        multi_search_instance.execute.return_value = ['data', 'data']
        query = self.instance.get_base_query()
        queries = (query, query)
        result = self.instance.make_multisearch_query_for_aggs(queries)
        self.assertListEqual(result, ['data', 'data'])

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_multisearch_query_for_aggs_single_item(self, multi_search):
        multi_search_instance = multi_search.return_value
        multi_search_instance.add.return_value = multi_search_instance
        multi_search_instance.execute.return_value = [{}]
        result = self.instance.make_multisearch_query_for_aggs(tuple(), flat=True)
        self.assertDictEqual(result, dict())

    def test_get_histogram_query(self):
        field = 'field'
        interval = 'day'
        date_format = 'yyyy-MM-dd'
        time_zone = 'timezone'
        result = self.instance.get_histogram_query(field, interval, date_format, time_zone)
        expected = {
            'from': 0,
            'aggs': {'unique': {'date_histogram': {'field': 'field', 'interval': 'day', 'time_zone': u'timezone',
                                                   'format': 'yyyy-MM-dd'}}},
            'size': 0
        }
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_unique_list_query(self):
        field = 'field'
        result = self.instance.get_unique_list_query(field)
        expected = {
            'from': 0,
            'aggs': {'unique': {'terms': {'field': 'field', 'size': 0}}},
            'size': 0
        }
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper.get_histogram_query')
    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper.make_multisearch_query_for_aggs')
    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper.get_attr_list')
    def test_available_days_with_valid_operators(self, get_attr_list, make_multisearch_query_for_aggs,
                                                 get_histogram_query):
        get_histogram_query.return_value = self.instance.get_base_query()
        make_multisearch_query_for_aggs.return_value = []
        get_attr_list.return_value = []
        result = self.instance._get_available_days('field', [1, 2, 3])
        self.assertListEqual(result, [])

    def test_get_data_by_file(self):
        file_filter = 'file_filter'
        result = self.instance.get_data_by_file(file_filter)
        expected = {'query': {'bool': {'filter': [{'terms': {'path': u'file_filter'}}]}}, 'from': 0,
                    'aggs': {'files': {'terms': {'field': 'path', 'size': 5000}}}, 'size': 0}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.Search')
    def test_delete_data_by_file(self, search):
        file_name = 'file'
        search.return_value = search
        search.filter.return_value = search
        search.delete.return_value = 1
        result = self.instance.delete_data_by_file(file_name)
        self.assertIsInstance(result, int)

    @mock.patch('esapi.helper.basehelper.Search')
    def test_delete_data_by_file_exception(self, search):
        file_name = 'file'
        search.return_value = search
        search.filter.return_value = search
        search.delete.side_effect = ConnectionTimeout()
        result = self.instance.delete_data_by_file(file_name)
        self.assertIsNone(result)
