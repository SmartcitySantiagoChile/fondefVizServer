from unittest import mock

from django.test import TestCase
from elasticsearch_dsl import Search

from esapi.errors import ESQueryDateRangeParametersDoesNotExist, ESQueryStagesEmpty, ESQueryTooManyOriginZonesError, \
    ESQueryDestinationZoneParameterDoesNotExist, \
    ESQueryTooManyDestinationZonesError, ESQueryStopParameterDoesNotExist
from esapi.helper.trip import ESTripHelper


class ESTripIndexTest(TestCase):

    def setUp(self):
        self.instance = ESTripHelper()

    def test__build_histogram_query(self):
        base_es_query = Search()
        result = self.instance._build_histogram_query(base_es_query)
        expected = {'aggs': {'distancia_ruta': {'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                                         'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                                                'histogram': {'field': 'distancia_ruta', 'interval': '5000',
                                                              'min_doc_count': 0,
                                                              'extended_bounds': {'max': 30000, 'min': 0}}},
                             'n_etapas': {
                                 'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                          'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                                 'histogram': {'field': 'n_etapas', 'interval': '1', 'min_doc_count': 0,
                                               'extended_bounds': {'max': 5, 'min': 1}}}, 'distancia_eucl': {
                'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                         'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                'histogram': {'field': 'distancia_eucl', 'interval': '5000', 'min_doc_count': 0,
                              'extended_bounds': {'max': 30000, 'min': 0}}}, 'tviaje': {
                'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                         'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                'histogram': {'field': 'tviaje', 'interval': '15', 'min_doc_count': 0,
                              'extended_bounds': {'max': 120, 'min': 0}}}}}
        self.assertDictEqual(result.to_dict(), expected)

    def test__build_indicators_query(self):
        base_es_query = Search()
        result = self.instance._build_indicators_query(base_es_query)
        expected = {'aggs': {'viajes': {'sum': {'field': 'factor_expansion'}},
                             'distancia_ruta': {'stats': {'field': 'distancia_ruta'}},
                             'tviaje': {'stats': {'field': 'tviaje'}},
                             'distancia_eucl': {'stats': {'field': 'distancia_eucl'}},
                             'n_etapas': {'stats': {'field': 'n_etapas'}},
                             'documentos': {'value_count': {'field': 'n_etapas'}}}}
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_resume_data_query(self):
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        origin_zones = [1, 2, 3]
        destination_zones = [3, 2, 1]
        dates = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_resume_data_query,
                          dates, day_types, periods, origin_zones, destination_zones)
        dates = [["2018-01-01", "2018-02-01"]]
        result = self.instance.get_base_resume_data_query(dates, day_types, periods, origin_zones,
                                                          destination_zones)
        expected = {'query': {'bool': {'filter': [
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'range': {
                'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                                  'format': 'yyyy-MM-dd'}}},
        ]}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.trip.ESTripHelper.get_base_resume_data_query')
    def test_get_resume_data(self, mock_method):
        dates = '[["2018-01-01", "2018-02-01"]]'
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        origin_zones = [1, 2, 3]
        destination_zones = [3, 2, 1]
        mock_method.return_value = Search()
        hist_query, ind_query = self.instance.get_resume_data(dates, day_types, periods, origin_zones,
                                                              destination_zones)
        expected1 = {'from': 0, 'aggs': {'distancia_ruta': {'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                                                     'total': {
                                                                         'cumulative_sum': {'buckets_path': 'bin'}}},
                                                            'histogram': {'field': 'distancia_ruta',
                                                                          'interval': '5000', 'min_doc_count': 0,
                                                                          'extended_bounds': {'max': 30000,
                                                                                              'min': 0}}},
                                         'n_etapas': {'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                                               'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                                                      'histogram': {'field': 'n_etapas', 'interval': '1',
                                                                    'min_doc_count': 0,
                                                                    'extended_bounds': {'max': 5, 'min': 1}}},
                                         'distancia_eucl': {'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                                                     'total': {
                                                                         'cumulative_sum': {'buckets_path': 'bin'}}},
                                                            'histogram': {'field': 'distancia_eucl',
                                                                          'interval': '5000', 'min_doc_count': 0,
                                                                          'extended_bounds': {'max': 30000,
                                                                                              'min': 0}}},
                                         'tviaje': {'aggs': {'bin': {'sum': {'field': 'factor_expansion'}},
                                                             'total': {'cumulative_sum': {'buckets_path': 'bin'}}},
                                                    'histogram': {'field': 'tviaje', 'interval': '15',
                                                                  'min_doc_count': 0,
                                                                  'extended_bounds': {'max': 120, 'min': 0}}}},
                     'size': 0}
        expected2 = {'from': 0, 'aggs': {'viajes': {'sum': {'field': 'factor_expansion'}},
                                         'distancia_ruta': {'stats': {'field': 'distancia_ruta'}},
                                         'tviaje': {'stats': {'field': 'tviaje'}},
                                         'distancia_eucl': {'stats': {'field': 'distancia_eucl'}},
                                         'n_etapas': {'stats': {'field': 'n_etapas'}},
                                         'documentos': {'value_count': {'field': 'n_etapas'}}}, 'size': 0}

        self.assertIsInstance(hist_query, Search)
        self.assertDictEqual(hist_query.to_dict(), expected1)
        self.assertIsInstance(ind_query, Search)
        self.assertDictEqual(ind_query.to_dict(), expected2)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days()
        self.assertListEqual(result, [])

    def test_get_base_map_data_query(self):
        dates = [[""]]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        sectors = [1, 2, 3]
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_map_data_query, dates,
                          day_types, periods, sectors)
        dates = [["2018-01-01", "2018-02-01"]]
        result = self.instance.get_base_map_data_query(dates, day_types, periods, sectors)
        expected = {'query': {'bool': {'filter': [
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'range': {
                'tiempo_subida': {'time_zone': '+00:00',
                                  'gte': '2018-01-01||/d',
                                  'lte': '2018-02-01||/d',
                                  'format': 'yyyy-MM-dd'}}}

        ]}}}
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_map_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        sectors = {'key1': 'value'}
        result = self.instance.get_map_data(dates, day_types, periods, sectors)
        expected = {'query': {'bool': {'filter': [
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'range': {
                'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                                  'format': 'yyyy-MM-dd'}}},
        ]}},
            'from': 0, 'aggs': {
                'key1': {'filter': {'terms': {'zona_bajada': 'value'}},
                         'aggs': {
                             'by_zone': {'terms': {'field': 'zona_subida', 'size': 1000},
                                         'aggs': {'distancia_ruta': {'avg': {'field': 'distancia_ruta'}},
                                                  'n_etapas': {'avg': {'field': 'n_etapas'}},
                                                  'expansion_factor': {'sum': {'field': 'factor_expansion'}},
                                                  'distancia_eucl': {'avg': {'field': 'distancia_eucl'}},
                                                  'tviaje': {'avg': {'field': 'tviaje'}}}}}},
                'sum_expansion_factor': {'sum': {'field': 'factor_expansion'}}}, 'size': 0}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_large_travel_data_query_five_stages(self):
        dates = [[]]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        n_etapas = [1, 2, 3, 4, '5+']
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_large_travel_data_query,
                          dates, day_types, periods, n_etapas)
        dates = [['2018-01-01', '2018-02-01']]
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}}], 'minimum_should_match': 1,
            'should': [{'terms': {'n_etapas': [1, 2, 3, 4]}},
                       {'range': {'n_etapas': {'gte': 5}}}]}}}

        result = self.instance.get_base_large_travel_data_query(dates, day_types, periods, n_etapas)
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_large_travel_data_query(self):
        dates = []
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        n_etapas = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_large_travel_data_query,
                          dates, day_types, periods, n_etapas)
        dates = [['2018-01-01', '2018-02-01']]
        self.assertRaises(ESQueryStagesEmpty, self.instance.get_base_large_travel_data_query, dates,
                          day_types, periods, n_etapas)
        n_etapas = [1, 2, 3, 4]
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [1, 2, 3, 4]}}]}}}

        result = self.instance.get_base_large_travel_data_query(dates, day_types, periods, n_etapas)
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_large_travel_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        n_etapas = [1, 2, 3, 4]
        origin_or_destination = 'destination'
        result = self.instance.get_large_travel_data(dates, day_types, periods, n_etapas,
                                                     origin_or_destination)
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [1, 2, 3, 4]}}]}}, 'from': 0,
            'aggs': {'sum_expansion_factor': {'sum': {'field': 'factor_expansion'}},
                     'by_zone': {'terms': {'field': 'zona_bajada', 'size': 1000},
                                 'aggs': {'distancia_ruta': {'avg': {'field': 'distancia_ruta'}},
                                          'n_etapas': {'avg': {'field': 'n_etapas'}},
                                          'expansion_factor': {'sum': {'field': 'factor_expansion'}},
                                          'distancia_eucl': {'avg': {'field': 'distancia_eucl'}},
                                          'tviaje': {'avg': {'field': 'tviaje'}}}}}, 'size': 0}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_from_to_map_data_query(self):
        dates = [[""]]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        minutes = [1, 2, 3]
        stages = [4, 3, 2, 1]
        modes = 'modes'
        origin_zones = [1, 2, 3]
        destination_zones = [3, 2, 1]
        routes = 'authRoutes[]'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_from_to_map_data_query,
                          dates, day_types, periods, minutes, stages, modes, origin_zones,
                          destination_zones, routes)
        dates = ['2018-01-01', '2018-02-01']
        result = self.instance.get_base_from_to_map_data_query(dates, day_types, periods, minutes,
                                                               stages, modes, origin_zones, destination_zones, routes)
        expected = {'query': {'bool': {'filter': [{'bool': {'should': [
            {'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                         'format': 'yyyy-MM-dd'}}},
            {'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                         'format': 'yyyy-MM-dd'}}}]}},
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': 'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'bool': {'should': [{'terms': {'srv_4': 'authRoutes[]'}},
                                 {'terms': {'srv_3': 'authRoutes[]'}},
                                 {'terms': {'srv_2': 'authRoutes[]'}},
                                 {'terms': {'srv_1': 'authRoutes[]'}}]
                      }}]}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_from_to_map_data(self):
        dates = ['2018-01-01', '2018-02-01']
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        minutes = [1, 2, 3]
        stages = [4, 3, 2, 1]
        modes = 'modes'
        origin_zones = [1, 2, 3]
        destination_zones = [3, 2, 1]
        routes = ''
        result1, result2 = self.instance.get_from_to_map_data(dates, day_types, periods, minutes, stages,
                                                              modes,
                                                              origin_zones, destination_zones, routes)
        expected1 = {'query': {'bool': {'filter': [
            {'bool':
                 {'should':
                      [{'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                                    'format': 'yyyy-MM-dd'}}},
                       {'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                                    'format': 'yyyy-MM-dd'}}}]
                  }},
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': 'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0,
            'aggs': {'expansion_factor': {'sum': {'field': 'factor_expansion'}},
                     'by_zone': {'terms': {'field': 'zona_subida', 'size': 1000},
                                 'aggs': {'distancia_ruta': {'avg': {'field': 'distancia_ruta'}},
                                          'n_etapas': {'avg': {'field': 'n_etapas'}},
                                          'expansion_factor': {'sum': {'field': 'factor_expansion'}},
                                          'distancia_eucl': {'avg': {'field': 'distancia_eucl'}},
                                          'tviaje': {'avg': {'field': 'tviaje'}}}}}, 'size': 0}

        expected2 = {'query': {'bool': {'filter': [
            {'bool':
                 {'should':
                      [{'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                                    'format': 'yyyy-MM-dd'}}},
                       {'range': {'tiempo_subida': {'time_zone': '+00:00', 'gte': '2||/d', 'lte': '1||/d',
                                                    'format': 'yyyy-MM-dd'}}}]
                  }},
            {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': 'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0, 'aggs': {
            'by_zone': {'terms': {'field': 'zona_bajada', 'size': 1000},
                        'aggs': {'distancia_ruta': {'avg': {'field': 'distancia_ruta'}},
                                 'n_etapas': {'avg': {'field': 'n_etapas'}},
                                 'expansion_factor': {'sum': {'field': 'factor_expansion'}},
                                 'distancia_eucl': {'avg': {'field': 'distancia_eucl'}},
                                 'tviaje': {'avg': {'field': 'tviaje'}}}}}, 'size': 0}
        self.assertDictEqual(result1.to_dict(), expected1)
        self.assertDictEqual(result2.to_dict(), expected2)

    def test_get_base_strategies_data_query(self):
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        minutes = [1, 2, 3]
        destination_zones = []
        routes = ['a', 'b', 'c']
        dates = []
        origin_zones = [None] * 51
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_strategies_data_query,
                          dates, day_types, periods, minutes, origin_zones,
                          destination_zones, routes)
        dates = [['2018-01-01', '2018-02-01']]
        self.assertRaises(ESQueryTooManyOriginZonesError, self.instance.get_base_strategies_data_query,
                          dates, day_types, periods, minutes, origin_zones,
                          destination_zones, routes)
        origin_zones = [1, 2, 3]
        self.assertRaises(ESQueryDestinationZoneParameterDoesNotExist, self.instance.get_base_strategies_data_query,
                          dates, day_types, periods, minutes, origin_zones,
                          destination_zones, routes)
        destination_zones = [None] * 51
        self.assertRaises(ESQueryTooManyDestinationZonesError, self.instance.get_base_strategies_data_query,
                          dates, day_types, periods, minutes, origin_zones,
                          destination_zones, routes)
        destination_zones = [3, 2, 1]
        result = self.instance.get_base_strategies_data_query(dates, day_types, periods, minutes,
                                                              origin_zones, destination_zones, routes)

        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'bool': {'should': [{'terms': {'srv_1': ['a', 'b', 'c']}}, {'terms': {'srv_2': ['a', 'b', 'c']}},
                                 {'terms': {'srv_3': ['a', 'b', 'c']}},
                                 {'terms': {'srv_4': ['a', 'b', 'c']}}
                                 ]}}]}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_strategies_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        minutes = [1, 2, 3]
        origin_zones = [1, 2, 3]
        destination_zones = [3, 2, 1]
        routes = ''
        result = self.instance.get_strategies_data(dates, day_types, periods, minutes,
                                                   origin_zones, destination_zones, routes)
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'terms': {'tipodia': ['LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0, 'aggs': {
            'a': {'filter': {'bool': {'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}]}}, 'aggs': {
                'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                            'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                    'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}},
            'c': {'filter': {'bool': {'filter': [{'terms': {'tipo_transporte_3': [2, 4]}}]}}, 'aggs': {
                'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                        'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                            'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                    'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}},
            'b': {'filter': {'bool': {'filter': [{'terms': {'tipo_transporte_2': [2, 4]}}]}}, 'aggs': {
                'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                        'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                            'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                    'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}, 'e': {
                'filter': {'bool': {
                    'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}}]}},
                'aggs': {'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                            'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                                'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                    'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'd': {'filter': {'bool': {'filter': [{'terms': {'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                        'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                            'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000}, 'aggs': {
                                    'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}, 'g': {
                'filter': {'bool': {
                    'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                            'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                    'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000}, 'aggs': {
                                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'f': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_3': [2, 4]}}]}},
                'aggs': {'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                            'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'strategies_without_metro_or_metrotren': {'filter': {'bool': {'must_not': [{'bool': {
                'should': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}},
                           {'terms': {'tipo_transporte_3': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}}]}},
                'aggs': {'first': {'terms': {'field': 'srv_1', 'size': 2000},
                                   'aggs': {'second': {
                                       'terms': {'field': 'srv_2',
                                                 'size': 2000}, 'aggs': {
                                           'third': {
                                               'terms': {'field': 'srv_3',
                                                         'size': 2000},
                                               'aggs': {'fourth': {
                                                   'terms': {'field': 'srv_4',
                                                             'size': 2000},
                                                   'aggs': {
                                                       'expansion_factor': {
                                                           'sum': {
                                                               'field': 'factor_expansion'}}}}}}}}}}}},
            'h': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_2': [2, 4]}}, {'terms': {'tipo_transporte_3': [2, 4]}}]}},
                'aggs': {'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                        'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                            'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'k': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}},
                           {'terms': {'tipo_transporte_3': [2, 4]}}]}}, 'aggs': {
                'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                            'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                                'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                    'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                        'fourth': {'terms': {'field': 'srv_4', 'size': 2000}, 'aggs': {
                                            'expansion_factor': {
                                                'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}}}}, 'j': {
                'filter': {'bool': {
                    'filter': [{'terms': {'tipo_transporte_3': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                        'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                            'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                    'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000}, 'aggs': {
                                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'm': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_3': [2, 4]}},
                           {'terms': {'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'second': {'terms': {'field': 'srv_2', 'size': 2000}, 'aggs': {
                            'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                        'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000},
                                                          'aggs': {'expansion_factor': {
                                                              'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}}}},
            'l': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}},
                           {'terms': {'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                            'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                                'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                    'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                        'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000},
                                                          'aggs': {'expansion_factor': {
                                                              'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}}}},
            'o': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}},
                           {'terms': {'tipo_transporte_3': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {'start_station_1': {'terms': {'field': 'parada_subida_1', 'size': 5000}, 'aggs': {
                    'end_station_1': {'terms': {'field': 'parada_bajada_1', 'size': 5000}, 'aggs': {
                        'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                            'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                                'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                    'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000},
                                                      'aggs': {'start_station_4': {
                                                          'terms': {'field': 'parada_subida_4', 'size': 5000},
                                                          'aggs': {'end_station_4': {
                                                              'terms': {'field': 'parada_bajada_4', 'size': 5000},
                                                              'aggs': {'expansion_factor': {'sum': {
                                                                  'field': 'factor_expansion'}}}}}}}}}}}}}}}}}}}},
            'n': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_2': [2, 4]}}, {'terms': {'tipo_transporte_3': [2, 4]}},
                           {'terms': {'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                        'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                            'start_station_3': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                                'end_station_3': {'terms': {'field': 'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                        'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000},
                                                          'aggs': {'expansion_factor': {
                                                              'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}}}},
            'i': {'filter': {'bool': {
                'filter': [{'terms': {'tipo_transporte_2': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {'first': {'terms': {'field': 'srv_1', 'size': 2000}, 'aggs': {
                    'start_station_2': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                        'end_station_2': {'terms': {'field': 'parada_bajada_2', 'size': 5000}, 'aggs': {
                            'third': {'terms': {'field': 'srv_3', 'size': 2000}, 'aggs': {
                                'start_station_4': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                                    'end_station_4': {'terms': {'field': 'parada_bajada_4', 'size': 5000},
                                                      'aggs': {'expansion_factor': {
                                                          'sum': {'field': 'factor_expansion'}}}}}}}}}}}}}}}},
            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}, 'size': 0}
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_transfers_data_query(self):
        dates = [[""]]
        auth_stop_code = ''
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        half_hours = [1, 2, 3]
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_base_transfers_data_query,
                          dates, auth_stop_code, day_types, periods, half_hours)
        auth_stop_code = 'auth_stop_code'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_base_transfers_data_query,
                          dates, auth_stop_code, day_types, periods, half_hours)
        dates = [['2018-01-01', '2018-02-01']]
        result = self.instance.get_base_transfers_data_query(dates, auth_stop_code, day_types, periods,
                                                             half_hours)
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'bool': {
            'should': [{'term': {'parada_bajada_1': 'auth_stop_code'}},
                       {'term': {'parada_bajada_2': 'auth_stop_code'}},
                       {'term': {'parada_bajada_3': 'auth_stop_code'}},
                       {'term': {'parada_bajada_4': 'auth_stop_code'}}]}}, {'terms': {'tipodia': ['LABORAL']}}, {
            'bool': {'should': [{'terms': {'periodo_bajada_1': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_2': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_3': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_4': [1, 2, 3]}}]}},
            {'bool': {'should': [{'terms': {'mediahora_bajada_1': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_2': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_3': [1, 2, 3]}}, {
                                     'terms': {
                                         'mediahora_bajada_4': [1, 2, 3]}}]}}]}}}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_transfers_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        auth_stop_code = 'auth_stop_code'
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        half_hours = [1, 2, 3]
        result = self.instance.get_transfers_data(dates, auth_stop_code, day_types, periods, half_hours)
        expected = {'query': {'bool': {'filter': [{'range': {
            'tiempo_subida': {'time_zone': '+00:00', 'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d',
                              'format': 'yyyy-MM-dd'}}}, {'bool': {
            'should': [{'term': {'parada_bajada_1': 'auth_stop_code'}},
                       {'term': {'parada_bajada_2': 'auth_stop_code'}},
                       {'term': {'parada_bajada_3': 'auth_stop_code'}},
                       {'term': {'parada_bajada_4': 'auth_stop_code'}}]}}, {'terms': {'tipodia': ['LABORAL']}}, {
            'bool': {'should': [{'terms': {'periodo_bajada_1': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_2': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_3': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_4': [1, 2, 3]}}]}},
            {'bool': {'should': [{'terms': {'mediahora_bajada_1': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_2': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_3': [1, 2, 3]}}, {
                                     'terms': {
                                         'mediahora_bajada_4': [1, 2, 3]}}]}}]}},
            'aggs': {'second_transfer': {'filter': {'bool': {
                'must': [{'term': {'parada_bajada_2': 'auth_stop_code'}},
                         {'range': {'n_etapas': {'gt': 2}}}]}}, 'aggs': {
                'route_from': {'terms': {'field': 'srv_2', 'size': 5000}, 'aggs': {
                    'route_to': {'terms': {'field': 'srv_3', 'size': 5000},
                                 'aggs': {'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'third_transfer_to_subway': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_3': 'auth_stop_code'}},
                             {'range': {'n_etapas': {'gt': 3}}}, {'term': {'tipo_transporte_4': 2}},
                             {'term': {'tipo_transporte_4': 4}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_3', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'parada_subida_4', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'first_transfer': {'filter': {'bool': {'must': [{'term': {
                    'parada_bajada_1': 'auth_stop_code'}},
                    {'range': {'n_etapas': {'gt': 1}}}]}},
                    'aggs': {'route_from': {'terms': {'field': 'srv_1', 'size': 5000},
                                            'aggs': {'route_to': {
                                                'terms': {'field': 'srv_2',
                                                          'size': 5000}, 'aggs': {
                                                    'expansion_factor': {'sum': {
                                                        'field': 'factor_expansion'}}}}}}}},
                'second_transfer_to_subway': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_2': 'auth_stop_code'}},
                             {'range': {'n_etapas': {'gt': 2}}}, {'term': {'tipo_transporte_3': 2}},
                             {'term': {'tipo_transporte_3': 4}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_2', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'parada_subida_3', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'fourth_transfer_is_end': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_4': 'auth_stop_code'}},
                             {'term': {'n_etapas': 4}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_4', 'size': 5000}, 'aggs': {
                        'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}},
                'first_transfer_is_end': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_1': 'auth_stop_code'}},
                             {'term': {'n_etapas': 1}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_1', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'srv_2', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'third_transfer_is_end': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_3': 'auth_stop_code'}},
                             {'term': {'n_etapas': 3}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_3', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'srv_4', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'third_transfer': {'filter': {'bool': {'must': [{'term': {
                    'parada_bajada_3': 'auth_stop_code'}},
                    {'range': {'n_etapas': {'gt': 3}}}]}},
                    'aggs': {'route_from': {'terms': {'field': 'srv_3', 'size': 5000},
                                            'aggs': {'route_to': {
                                                'terms': {'field': 'srv_4',
                                                          'size': 5000}, 'aggs': {
                                                    'expansion_factor': {'sum': {
                                                        'field': 'factor_expansion'}}}}}}}},
                'second_transfer_is_end': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_2': 'auth_stop_code'}},
                             {'term': {'n_etapas': 2}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_2', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'srv_3', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}},
                'first_transfer_to_subway': {'filter': {'bool': {
                    'must': [{'term': {'parada_bajada_1': 'auth_stop_code'}},
                             {'range': {'n_etapas': {'gt': 1}}}, {'term': {'tipo_transporte_2': 2}},
                             {'term': {'tipo_transporte_2': 4}}]}}, 'aggs': {
                    'route_from': {'terms': {'field': 'srv_1', 'size': 5000}, 'aggs': {
                        'route_to': {'terms': {'field': 'parada_subida_2', 'size': 5000}, 'aggs': {
                            'expansion_factor': {'sum': {'field': 'factor_expansion'}}}}}}}}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_all_time_periods(self):
        expected_query = {'aggs': {'time_periods_per_file': {'terms': {'field': 'path', 'size': 5000}, 'aggs': {
            'time_periods': {'terms': {'field': 'periodo_subida'}}}}}, 'from': 0, 'size': 0}
        result = self.instance.get_all_time_periods().to_dict()
        self.assertEqual(expected_query, result)
