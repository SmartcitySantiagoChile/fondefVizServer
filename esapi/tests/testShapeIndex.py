# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import mock

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

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper.get_base_query')
    def test_get_available_days(self, get_data_from_date):
        es_query = mock.MagicMock()
        es_query.filter.return_value = es_query
        es_query.update_from_dict.return_value = list()
        get_data_from_date.return_value = es_query
        result = self.instance.get_data_from_date('2020-01-01')
        self.assertListEqual(result, [])

    def test_convert_shape_to_speed_csv_format(self):
        shape = [{'segmentStart': 1, 'longitude': -70.681396, 'latitude': -33.363362},
                 {'segmentStart': 0, 'longitude': -70.6809, 'latitude': -33.367157},
                 {'segmentStart': 0, 'longitude': -70.681683, 'latitude': -33.366942},
                 {'segmentStart': 1, 'longitude': -70.684011, 'latitude': -33.366303},
                 {'segmentStart': 0, 'longitude': -70.686923, 'latitude': -33.366083},
                 {'segmentStart': 1, 'longitude': -70.689688, 'latitude': -33.365874},
                 {'segmentStart': 0, 'longitude': -70.688988, 'latitude': -33.367972},
                 {'segmentStart': 1, 'longitude': -70.687941, 'latitude': -33.37111},
                 {'segmentStart': 0, 'longitude': -70.687309, 'latitude': -33.372242},
                 {'segmentStart': 1, 'longitude': -70.685811, 'latitude': -33.374927},
                 {'segmentStart': 0, 'longitude': -70.684877, 'latitude': -33.376257},
                 {'segmentStart': 1, 'longitude': -70.684085, 'latitude': -33.377385},
                 {'segmentStart': 0, 'longitude': -70.683365, 'latitude': -33.3802},
                 {'segmentStart': 0, 'longitude': -70.683226, 'latitude': -33.380498},
                 {'segmentStart': 1, 'longitude': -70.682498, 'latitude': -33.38206},
                 {'segmentStart': 0, 'longitude': -70.680562, 'latitude': -33.38438},
                 {'segmentStart': 1, 'longitude': -70.680176, 'latitude': -33.384842},
                 {'segmentStart': 0, 'longitude': -70.678025, 'latitude': -33.388349},
                 {'segmentStart': 1, 'longitude': -70.677799, 'latitude': -33.388716},
                 {'segmentStart': 0, 'longitude': -70.676966, 'latitude': -33.388998},
                 {'segmentStart': 0, 'longitude': -70.676003, 'latitude': -33.389787},
                 {'segmentStart': 0, 'longitude': -70.674743, 'latitude': -33.391328},
                 {'segmentStart': 0, 'longitude': -70.674549, 'latitude': -33.391631},
                 {'segmentStart': 1, 'longitude': -70.672071, 'latitude': -33.395521},
                 {'segmentStart': 0, 'longitude': -70.672, 'latitude': -33.395599},
                 {'segmentStart': 1, 'longitude': -70.670523, 'latitude': -33.397219},
                 {'segmentStart': 0, 'longitude': -70.668442, 'latitude': -33.398965},
                 {'segmentStart': 1, 'longitude': -70.66575, 'latitude': -33.401225},
                 {'segmentStart': 0, 'longitude': -70.664821, 'latitude': -33.402283},
                 {'segmentStart': 1, 'longitude': -70.661635, 'latitude': -33.405914},
                 {'segmentStart': 1, 'longitude': -70.66153, 'latitude': -33.406034},
                 {'segmentStart': 0, 'longitude': -70.65971, 'latitude': -33.410118},
                 {'segmentStart': 1, 'longitude': -70.657827, 'latitude': -33.414341},
                 {'segmentStart': 1, 'longitude': -70.656487, 'latitude': -33.417347},
                 ]
        auth_code = 'T201 00I'
        expected_res = [['T201 00I', 1, -33.363362, -70.681396], ['T201 00I', 1, -33.367157, -70.6809],
                        ['T201 00I', 1, -33.366942, -70.681683], [['T201 00I', 1, -33.366303, -70.684011]],
                        ['T201 00I', 2, -33.366303, -70.684011], ['T201 00I', 2, -33.366083, -70.686923],
                        [['T201 00I', 2, -33.365874, -70.689688]], ['T201 00I', 3, -33.365874, -70.689688],
                        ['T201 00I', 3, -33.367972, -70.688988], [['T201 00I', 3, -33.37111, -70.687941]],
                        ['T201 00I', 4, -33.37111, -70.687941], ['T201 00I', 4, -33.372242, -70.687309],
                        [['T201 00I', 4, -33.374927, -70.685811]], ['T201 00I', 5, -33.374927, -70.685811],
                        ['T201 00I', 5, -33.376257, -70.684877], [['T201 00I', 5, -33.377385, -70.684085]],
                        ['T201 00I', 6, -33.377385, -70.684085], ['T201 00I', 6, -33.3802, -70.683365],
                        ['T201 00I', 6, -33.380498, -70.683226], [['T201 00I', 6, -33.38206, -70.682498]],
                        ['T201 00I', 7, -33.38206, -70.682498], ['T201 00I', 7, -33.38438, -70.680562],
                        [['T201 00I', 7, -33.384842, -70.680176]], ['T201 00I', 8, -33.384842, -70.680176],
                        ['T201 00I', 8, -33.388349, -70.678025], [['T201 00I', 8, -33.388716, -70.677799]],
                        ['T201 00I', 9, -33.388716, -70.677799], ['T201 00I', 9, -33.388998, -70.676966],
                        ['T201 00I', 9, -33.389787, -70.676003], ['T201 00I', 9, -33.391328, -70.674743],
                        ['T201 00I', 9, -33.391631, -70.674549], [['T201 00I', 9, -33.395521, -70.672071]],
                        ['T201 00I', 10, -33.395521, -70.672071], ['T201 00I', 10, -33.395599, -70.672],
                        [['T201 00I', 10, -33.397219, -70.670523]], ['T201 00I', 11, -33.397219, -70.670523],
                        ['T201 00I', 11, -33.398965, -70.668442], [['T201 00I', 11, -33.401225, -70.66575]],
                        ['T201 00I', 12, -33.401225, -70.66575], ['T201 00I', 12, -33.402283, -70.664821],
                        [['T201 00I', 12, -33.405914, -70.661635]], ['T201 00I', 13, -33.405914, -70.661635],
                        [['T201 00I', 13, -33.406034, -70.66153]], ['T201 00I', 14, -33.406034, -70.66153],
                        ['T201 00I', 14, -33.410118, -70.65971], [['T201 00I', 14, -33.414341, -70.657827]],
                        ['T201 00I', 15, -33.414341, -70.657827], [['T201 00I', 15, -33.417347, -70.656487]],
                        ['T201 00I', 16, -33.417347, -70.656487], ['T201 00I', 16, -33.417347, -70.656487]]

        self.assertEqual(expected_res, self.instance.convert_shape_to_speed_csv_format(shape, auth_code))
