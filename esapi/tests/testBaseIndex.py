# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings

from mock import mock

from elasticsearch_dsl import Search

from esapi.helper.basehelper import ElasticSearchHelper


class IndexNameTest(TestCase):

    @mock.patch('esapi.helper.basehelper.settings')
    def test_wrong_index_name(self, settings):
        settings.ES_CLIENT.return_value = None
        fail_name = None
        self.assertRaises(ValueError, ElasticSearchHelper, fail_name)
        other_fail_name = ''
        self.assertRaises(ValueError, ElasticSearchHelper, other_fail_name)

    @mock.patch('esapi.helper.basehelper.settings')
    def test_good_index_name(self, settings):
        settings.ES_CLIENT.return_value = None
        name = 'goodIndexName'
        self.assertIsInstance(ElasticSearchHelper(name), ElasticSearchHelper)


@override_settings(ES_CLIENT=mock.MagicMock())
class BaseIndexTest(TestCase):

    def setUp(self):
        self.name = 'goodIndexName'
        self.instance = ElasticSearchHelper(self.name)

    def test_get_base_query(self):
        query = self.instance.get_base_query()
        self.assertIsInstance(query, Search)

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_multisearch_query_for_aggs_without_docs(self, multi_search):
        mock_instance = multi_search.return_value
        mock_instance.add.return_value = mock_instance

        mock_tag = mock.Mock()
        type(mock_tag).doc_count = mock.PropertyMock(return_value=0)

        mock_item = mock.Mock()
        type(mock_item).aggregations = mock.PropertyMock(return_value=mock_item)
        type(mock_item).unique = mock.PropertyMock(return_value=mock_item)
        type(mock_item).buckets = mock.PropertyMock(return_value=[mock_tag])
        mock_instance.execute.return_value = [mock_item]

        queries = {
            'query1': self.instance.get_base_query()
        }
        result = self.instance.make_multisearch_query_for_aggs(queries)
        mock_instance.execute.assert_called_once()
        self.assertDictEqual(result, {'query1': []})

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_multisearch_query_for_aggs_with_docs_with_key_as_string(self, multi_search):
        mock_instance = multi_search.return_value
        mock_instance.add.return_value = mock_instance

        mock_tag = mock.Mock()
        type(mock_tag).doc_count = mock.PropertyMock(return_value=1)
        mock_tag.__iter__ = mock.Mock(return_value=iter(['key_as_string']))
        type(mock_tag).key_as_string = mock.PropertyMock(return_value='key')

        mock_item = mock.Mock()
        type(mock_item).aggregations = mock.PropertyMock(return_value=mock_item)
        type(mock_item).unique = mock.PropertyMock(return_value=mock_item)
        type(mock_item).buckets = mock.PropertyMock(return_value=[mock_tag])
        mock_instance.execute.return_value = [mock_item]

        queries = {
            'query1': self.instance.get_base_query()
        }
        result = self.instance.make_multisearch_query_for_aggs(queries)
        mock_instance.execute.assert_called_once()
        self.assertDictEqual(result, {'query1': ['key']})

    @mock.patch('esapi.helper.basehelper.MultiSearch')
    def test_multisearch_query_for_aggs_with_docs_without_key_as_string(self, multi_search):
        mock_instance = multi_search.return_value
        mock_instance.add.return_value = mock_instance

        mock_tag = mock.Mock()
        type(mock_tag).doc_count = mock.PropertyMock(return_value=1)
        mock_tag.__iter__ = mock.Mock(return_value=iter([]))
        type(mock_tag).key = mock.PropertyMock(return_value='key')

        mock_item = mock.Mock()
        type(mock_item).aggregations = mock.PropertyMock(return_value=mock_item)
        type(mock_item).unique = mock.PropertyMock(return_value=mock_item)
        type(mock_item).buckets = mock.PropertyMock(return_value=[mock_tag])
        mock_instance.execute.return_value = [mock_item]

        queries = {
            'query1': self.instance.get_base_query()
        }
        result = self.instance.make_multisearch_query_for_aggs(queries)
        mock_instance.execute.assert_called_once()
        self.assertDictEqual(result, {'query1': ['key']})

    def test_get_histogram_query(self):
        field = 'field'
        interval = 'day'
        date_format = 'yyyy-MM-dd'

        result = self.instance.get_histogram_query(field, interval, date_format)

        expected_query = {
            'query': {'match_all': {}}, 'from': 0,
            'aggs': {'unique': {'date_histogram': {'field': 'field', 'interval': 'day', 'format': 'yyyy-MM-dd'}}},
            'size': 0
        }
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected_query)

    def test_get_unique_list_query(self):
        field = 'field'
        size = 10
        # first call with query argument as null
        result = self.instance.get_unique_list_query(field, size)

        expected_query = {
            'aggs': {'unique': {'terms': {'field': 'field', 'size': 10}}},
            'from': 0,
            'query': {'match_all': {}},
            'size': 0
        }
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected_query)
