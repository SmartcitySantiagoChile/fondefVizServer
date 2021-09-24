from unittest import mock

from django.test import TestCase

from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryStopInfoDoesNotExist, \
    ESQueryDateRangeParametersDoesNotExist
from esapi.helper.stop import ESStopHelper


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

    @mock.patch('esapi.helper.stop.ESStopHelper.make_multisearch_query_for_aggs')
    def test_get_matched_stop_list_with_date(self, make_multisearch_query_for_aggs):
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
        result = self.instance.get_matched_stop_list('term','date')
        self.assertListEqual(result, [('key', 'auth_code')])

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_stop_info(self, get_base_query):
        auth_stop_code = ''
        dates = [[]]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_stop_info, dates, auth_stop_code)
        dates = [["2018-01-01"]]
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_stop_info, dates, auth_stop_code)
        auth_stop_code = 'auth_stop_code'
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
        result = self.instance.get_stop_info(dates, auth_stop_code)
        self.assertDictEqual(result, {'key': 'value'})

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_stop_info_with_empty_stop_info(self, get_base_query):
        auth_stop_code = 'auth_stop_code'
        start_date = [['2018-01-01']]
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.sort.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        hit = mock.Mock()
        type(get_base_query).hits = mock.PropertyMock(return_value=hit)
        type(hit).hits = mock.PropertyMock(return_value=[])
        self.assertRaises(ESQueryStopInfoDoesNotExist, self.instance.get_stop_info, start_date, auth_stop_code)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_all_get_stop_info(self, get_base_query):
        date = ''
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_all_stop_info, date)
        date = "2018-01-01"
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.extra.return_value = get_base_query
        expected_result = {"1123"}
        get_base_query.scan.return_value = mock.MagicMock(to_dict=expected_result)
        result = self.instance.get_all_stop_info(date)
        self.assertEqual(result, [])

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_all_stop_info_with_empty_stop_info(self, get_base_query):
        start_date = '2018-01-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.extra.return_value = get_base_query
        get_base_query.scan = mock.Mock(side_effect=ESQueryStopInfoDoesNotExist())
        self.assertRaises(ESQueryStopInfoDoesNotExist, self.instance.get_all_stop_info, start_date)

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_all_get_stop_info_to_dict(self, get_base_query):
        date = ''
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_all_stop_info, date)
        date = "2018-01-01"
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.extra.return_value = get_base_query
        expected_result = {"1123"}
        get_base_query.scan.return_value = mock.MagicMock(to_dict=expected_result)
        result = self.instance.get_all_stop_info(date, to_dict=True)
        self.assertEqual(result, {})

    @mock.patch('esapi.helper.stop.ESStopHelper.get_base_query')
    def test_get_all_stop_info_with_empty_stop_info_to_dict(self, get_base_query):
        start_date = '2018-01-01'
        get_base_query.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.extra.return_value = get_base_query
        get_base_query.scan = mock.Mock(side_effect=ESQueryStopInfoDoesNotExist())
        self.assertRaises(ESQueryStopInfoDoesNotExist, self.instance.get_all_stop_info, start_date, to_dict=True)