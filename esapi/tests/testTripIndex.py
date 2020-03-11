# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
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
        expected = {'aggs': {u'distancia_ruta': {'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                                          u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                                                 'histogram': {'field': u'distancia_ruta', 'interval': u'5000',
                                                               'min_doc_count': 0,
                                                               'extended_bounds': {u'max': 30000, u'min': 0}}},
                             u'n_etapas': {
                                 'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                          u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                                 'histogram': {'field': u'n_etapas', 'interval': u'1', 'min_doc_count': 0,
                                               'extended_bounds': {u'max': 5, u'min': 1}}}, u'distancia_eucl': {
                'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                         u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                'histogram': {'field': u'distancia_eucl', 'interval': u'5000', 'min_doc_count': 0,
                              'extended_bounds': {u'max': 30000, u'min': 0}}}, u'tviaje': {
                'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                         u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                'histogram': {'field': u'tviaje', 'interval': u'15', 'min_doc_count': 0,
                              'extended_bounds': {u'max': 120, u'min': 0}}}}}
        self.assertDictEqual(result.to_dict(), expected)

    def test__build_indicators_query(self):
        base_es_query = Search()
        result = self.instance._build_indicators_query(base_es_query)
        expected = {'aggs': {u'viajes': {'sum': {'field': u'factor_expansion'}},
                             u'distancia_ruta': {'stats': {'field': u'distancia_ruta'}},
                             u'tviaje': {'stats': {'field': u'tviaje'}},
                             u'distancia_eucl': {'stats': {'field': u'distancia_eucl'}},
                             u'n_etapas': {'stats': {'field': u'n_etapas'}},
                             u'documentos': {'value_count': {'field': u'n_etapas'}}}}
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
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'range': {
                'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                                  u'format': u'yyyy-MM-dd'}}},
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
        expected1 = {'from': 0, 'aggs': {u'distancia_ruta': {'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                                                      u'total': {
                                                                          'cumulative_sum': {'buckets_path': u'bin'}}},
                                                             'histogram': {'field': u'distancia_ruta',
                                                                           'interval': u'5000', 'min_doc_count': 0,
                                                                           'extended_bounds': {u'max': 30000,
                                                                                               u'min': 0}}},
                                         u'n_etapas': {'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                                                u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                                                       'histogram': {'field': u'n_etapas', 'interval': u'1',
                                                                     'min_doc_count': 0,
                                                                     'extended_bounds': {u'max': 5, u'min': 1}}},
                                         u'distancia_eucl': {'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                                                      u'total': {
                                                                          'cumulative_sum': {'buckets_path': u'bin'}}},
                                                             'histogram': {'field': u'distancia_eucl',
                                                                           'interval': u'5000', 'min_doc_count': 0,
                                                                           'extended_bounds': {u'max': 30000,
                                                                                               u'min': 0}}},
                                         u'tviaje': {'aggs': {u'bin': {'sum': {'field': u'factor_expansion'}},
                                                              u'total': {'cumulative_sum': {'buckets_path': u'bin'}}},
                                                     'histogram': {'field': u'tviaje', 'interval': u'15',
                                                                   'min_doc_count': 0,
                                                                   'extended_bounds': {u'max': 120, u'min': 0}}}},
                     'size': 0}
        expected2 = {'from': 0, 'aggs': {u'viajes': {'sum': {'field': u'factor_expansion'}},
                                         u'distancia_ruta': {'stats': {'field': u'distancia_ruta'}},
                                         u'tviaje': {'stats': {'field': u'tviaje'}},
                                         u'distancia_eucl': {'stats': {'field': u'distancia_eucl'}},
                                         u'n_etapas': {'stats': {'field': u'n_etapas'}},
                                         u'documentos': {'value_count': {'field': u'n_etapas'}}}, 'size': 0}

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
        print(result.to_dict())
        expected = {'query': {'bool': {'filter': [
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'range': {
                'tiempo_subida': {u'time_zone': u'+00:00',
                                  u'gte': u'2018-01-01||/d',
                                  u'lte': u'2018-02-01||/d',
                                  u'format': u'yyyy-MM-dd'}}}

        ]}}}
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_map_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        day_types = ['LABORAL']
        periods = [1, 2, 3]
        sectors = {'key1': 'value'}
        result = self.instance.get_map_data(dates, day_types, periods, sectors)
        expected = {'query': {'bool': {'filter': [
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'range': {
                'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                                  u'format': u'yyyy-MM-dd'}}},
        ]}},
            'from': 0, 'aggs': {
                u'key1': {'filter': {'terms': {'zona_bajada': u'value'}},
                          'aggs': {
                              u'by_zone': {'terms': {'field': u'zona_subida', 'size': 1000},
                                           'aggs': {u'distancia_ruta': {'avg': {'field': u'distancia_ruta'}},
                                                    u'n_etapas': {'avg': {'field': u'n_etapas'}},
                                                    u'expansion_factor': {'sum': {'field': u'factor_expansion'}},
                                                    u'distancia_eucl': {'avg': {'field': u'distancia_eucl'}},
                                                    u'tviaje': {'avg': {'field': u'tviaje'}}}}}},
                u'sum_expansion_factor': {'sum': {'field': u'factor_expansion'}}}, 'size': 0}
        self.assertIsInstance(result, Search)
        print(result.to_dict())
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}}], 'minimum_should_match': 1,
            'should': [{'terms': {'n_etapas': [1, 2, 3, 4]}},
                       {'range': {'n_etapas': {u'gte': 5}}}]}}}

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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'terms': {'tipodia': [u'LABORAL']}},
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [1, 2, 3, 4]}}]}}, 'from': 0,
            'aggs': {u'sum_expansion_factor': {'sum': {'field': u'factor_expansion'}},
                     u'by_zone': {'terms': {'field': u'zona_bajada', 'size': 1000},
                                  'aggs': {u'distancia_ruta': {'avg': {'field': u'distancia_ruta'}},
                                           u'n_etapas': {'avg': {'field': u'n_etapas'}},
                                           u'expansion_factor': {'sum': {'field': u'factor_expansion'}},
                                           u'distancia_eucl': {'avg': {'field': u'distancia_eucl'}},
                                           u'tviaje': {'avg': {'field': u'tviaje'}}}}}, 'size': 0}

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
            {'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                         u'format': u'yyyy-MM-dd'}}},
            {'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                         u'format': u'yyyy-MM-dd'}}}]}},
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': u'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'bool': {'should': [{'terms': {u'srv_4': u'authRoutes[]'}},
                                 {'terms': {u'srv_3': u'authRoutes[]'}},
                                 {'terms': {u'srv_2': u'authRoutes[]'}},
                                 {'terms': {u'srv_1': u'authRoutes[]'}}]
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
                      [{'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                                    u'format': u'yyyy-MM-dd'}}},
                       {'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                                    u'format': u'yyyy-MM-dd'}}}]
                  }},
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': u'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0,
            'aggs': {u'expansion_factor': {'sum': {'field': u'factor_expansion'}},
                     u'by_zone': {'terms': {'field': u'zona_subida', 'size': 1000},
                                  'aggs': {u'distancia_ruta': {'avg': {'field': u'distancia_ruta'}},
                                           u'n_etapas': {'avg': {'field': u'n_etapas'}},
                                           u'expansion_factor': {'sum': {'field': u'factor_expansion'}},
                                           u'distancia_eucl': {'avg': {'field': u'distancia_eucl'}},
                                           u'tviaje': {'avg': {'field': u'tviaje'}}}}}, 'size': 0}

        expected2 = {'query': {'bool': {'filter': [
            {'bool':
                 {'should':
                      [{'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                                    u'format': u'yyyy-MM-dd'}}},
                       {'range': {'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2||/d', u'lte': u'1||/d',
                                                    u'format': u'yyyy-MM-dd'}}}]
                  }},
            {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'n_etapas': [4, 3, 2, 1]}},
            {'terms': {'modos': u'modes'}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0, 'aggs': {
            u'by_zone': {'terms': {'field': u'zona_bajada', 'size': 1000},
                         'aggs': {u'distancia_ruta': {'avg': {'field': u'distancia_ruta'}},
                                  u'n_etapas': {'avg': {'field': u'n_etapas'}},
                                  u'expansion_factor': {'sum': {'field': u'factor_expansion'}},
                                  u'distancia_eucl': {'avg': {'field': u'distancia_eucl'}},
                                  u'tviaje': {'avg': {'field': u'tviaje'}}}}}, 'size': 0}
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}},
            {'bool': {'should': [{'terms': {'srv_1': [u'a', u'b', u'c']}}, {'terms': {'srv_2': [u'a', u'b', u'c']}},
                                 {'terms': {'srv_3': [u'a', u'b', u'c']}},
                                 {'terms': {'srv_4': [u'a', u'b', u'c']}}
                                 ]}}]}}}
        print(result.to_dict())
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'terms': {'tipodia': [u'LABORAL']}},
            {'terms': {'periodo_subida': [1, 2, 3]}},
            {'terms': {'mediahora_subida': [1, 2, 3]}},
            {'terms': {'zona_subida': [1, 2, 3]}},
            {'terms': {'zona_bajada': [3, 2, 1]}}]}}, 'from': 0, 'aggs': {
            u'a': {'filter': {'bool': {u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}]}}, 'aggs': {
                u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                            u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                    u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}},
            u'c': {'filter': {'bool': {u'filter': [{'terms': {u'tipo_transporte_3': [2, 4]}}]}}, 'aggs': {
                u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                        u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                            u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                    u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}},
            u'b': {'filter': {'bool': {u'filter': [{'terms': {u'tipo_transporte_2': [2, 4]}}]}}, 'aggs': {
                u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                        u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                            u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                    u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}, u'e': {
                'filter': {'bool': {
                    u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_2': [2, 4]}}]}},
                'aggs': {u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                            u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                                u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                    u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'd': {'filter': {'bool': {u'filter': [{'terms': {u'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                        u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                            u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000}, 'aggs': {
                                    u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}, u'g': {
                'filter': {'bool': {
                    u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                            u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                    u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000}, 'aggs': {
                                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'f': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_3': [2, 4]}}]}},
                'aggs': {u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                            u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'strategies_without_metro_or_metrotren': {'filter': {'bool': {u'must_not': [{'bool': {
                u'should': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_2': [2, 4]}},
                            {'terms': {u'tipo_transporte_3': [2, 4]}}, {'terms': {u'tipo_transporte_4': [2, 4]}}]}}]}},
                'aggs': {u'first': {'terms': {'field': u'srv_1', 'size': 2000},
                                    'aggs': {u'second': {
                                        'terms': {'field': u'srv_2',
                                                  'size': 2000}, 'aggs': {
                                            u'third': {
                                                'terms': {'field': u'srv_3',
                                                          'size': 2000},
                                                'aggs': {u'fourth': {
                                                    'terms': {'field': u'srv_4',
                                                              'size': 2000},
                                                    'aggs': {
                                                        u'expansion_factor': {
                                                            'sum': {
                                                                'field': u'factor_expansion'}}}}}}}}}}}},
            u'h': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_2': [2, 4]}}, {'terms': {u'tipo_transporte_3': [2, 4]}}]}},
                'aggs': {u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                        u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                            u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'k': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_2': [2, 4]}},
                            {'terms': {u'tipo_transporte_3': [2, 4]}}]}}, 'aggs': {
                u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                            u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                                u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                    u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                        u'fourth': {'terms': {'field': u'srv_4', 'size': 2000}, 'aggs': {
                                            u'expansion_factor': {
                                                'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}}}}, u'j': {
                'filter': {'bool': {
                    u'filter': [{'terms': {u'tipo_transporte_3': [2, 4]}}, {'terms': {u'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                        u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                            u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                    u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000}, 'aggs': {
                                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'm': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_3': [2, 4]}},
                            {'terms': {u'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'second': {'terms': {'field': u'srv_2', 'size': 2000}, 'aggs': {
                            u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                        u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000},
                                                           'aggs': {u'expansion_factor': {
                                                               'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}}}},
            u'l': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_2': [2, 4]}},
                            {'terms': {u'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                            u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                                u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                    u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                        u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000},
                                                           'aggs': {u'expansion_factor': {
                                                               'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}}}},
            u'o': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_1': [2, 4]}}, {'terms': {u'tipo_transporte_2': [2, 4]}},
                            {'terms': {u'tipo_transporte_3': [2, 4]}}, {'terms': {u'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {u'start_station_1': {'terms': {'field': u'parada_subida_1', 'size': 5000}, 'aggs': {
                    u'end_station_1': {'terms': {'field': u'parada_bajada_1', 'size': 5000}, 'aggs': {
                        u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                            u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                                u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                    u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000},
                                                       'aggs': {u'start_station_4': {
                                                           'terms': {'field': u'parada_subida_4', 'size': 5000},
                                                           'aggs': {u'end_station_4': {
                                                               'terms': {'field': u'parada_bajada_4', 'size': 5000},
                                                               'aggs': {u'expansion_factor': {'sum': {
                                                                   'field': u'factor_expansion'}}}}}}}}}}}}}}}}}}}},
            u'n': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_2': [2, 4]}}, {'terms': {u'tipo_transporte_3': [2, 4]}},
                            {'terms': {u'tipo_transporte_4': [2, 4]}}]}}, 'aggs': {
                u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                        u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                            u'start_station_3': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                                u'end_station_3': {'terms': {'field': u'parada_bajada_3', 'size': 5000}, 'aggs': {
                                    u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                        u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000},
                                                           'aggs': {u'expansion_factor': {
                                                               'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}}}},
            u'i': {'filter': {'bool': {
                u'filter': [{'terms': {u'tipo_transporte_2': [2, 4]}}, {'terms': {u'tipo_transporte_4': [2, 4]}}]}},
                'aggs': {u'first': {'terms': {'field': u'srv_1', 'size': 2000}, 'aggs': {
                    u'start_station_2': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                        u'end_station_2': {'terms': {'field': u'parada_bajada_2', 'size': 5000}, 'aggs': {
                            u'third': {'terms': {'field': u'srv_3', 'size': 2000}, 'aggs': {
                                u'start_station_4': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                                    u'end_station_4': {'terms': {'field': u'parada_bajada_4', 'size': 5000},
                                                       'aggs': {u'expansion_factor': {
                                                           'sum': {'field': u'factor_expansion'}}}}}}}}}}}}}}}},
            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}, 'size': 0}
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'bool': {
            'should': [{'term': {'parada_bajada_1': u'auth_stop_code'}},
                       {'term': {'parada_bajada_2': u'auth_stop_code'}},
                       {'term': {'parada_bajada_3': u'auth_stop_code'}},
                       {'term': {'parada_bajada_4': u'auth_stop_code'}}]}}, {'terms': {'tipodia': [u'LABORAL']}}, {
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
            'tiempo_subida': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-02-01||/d',
                              u'format': u'yyyy-MM-dd'}}}, {'bool': {
            'should': [{'term': {'parada_bajada_1': u'auth_stop_code'}},
                       {'term': {'parada_bajada_2': u'auth_stop_code'}},
                       {'term': {'parada_bajada_3': u'auth_stop_code'}},
                       {'term': {'parada_bajada_4': u'auth_stop_code'}}]}}, {'terms': {'tipodia': [u'LABORAL']}}, {
            'bool': {'should': [{'terms': {'periodo_bajada_1': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_2': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_3': [1, 2, 3]}},
                                {'terms': {'periodo_bajada_4': [1, 2, 3]}}]}},
            {'bool': {'should': [{'terms': {'mediahora_bajada_1': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_2': [1, 2, 3]}},
                                 {'terms': {'mediahora_bajada_3': [1, 2, 3]}}, {
                                     'terms': {
                                         'mediahora_bajada_4': [1, 2, 3]}}]}}]}},
            'aggs': {u'second_transfer': {'filter': {'bool': {
                u'must_not': [{'term': {u'tipo_transporte_3': 2}}, {'term': {u'tipo_transporte_3': 4}}],
                u'must': [{'term': {u'parada_bajada_2': u'auth_stop_code'}},
                          {'range': {u'n_etapas': {u'gt': 2}}}]}}, 'aggs': {
                u'route_from': {'terms': {'field': u'srv_2', 'size': 5000}, 'aggs': {
                    u'route_to': {'terms': {'field': u'srv_3', 'size': 5000},
                                  'aggs': {u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'third_transfer_to_subway': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_3': u'auth_stop_code'}},
                              {'range': {u'n_etapas': {u'gt': 3}}}, {'term': {u'tipo_transporte_4': 2}},
                              {'term': {u'tipo_transporte_4': 4}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_3', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'parada_subida_4', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'first_transfer': {'filter': {'bool': {u'must_not': [{'term': {u'tipo_transporte_2': 2}},
                                                                      {'term': {u'tipo_transporte_2': 4}}],
                                                        u'must': [{'term': {
                                                            u'parada_bajada_1': u'auth_stop_code'}},
                                                            {'range': {u'n_etapas': {u'gt': 1}}}]}},
                                    'aggs': {u'route_from': {'terms': {'field': u'srv_1', 'size': 5000},
                                                             'aggs': {u'route_to': {
                                                                 'terms': {'field': u'srv_2',
                                                                           'size': 5000}, 'aggs': {
                                                                     u'expansion_factor': {'sum': {
                                                                         'field': u'factor_expansion'}}}}}}}},
                u'second_transfer_to_subway': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_2': u'auth_stop_code'}},
                              {'range': {u'n_etapas': {u'gt': 2}}}, {'term': {u'tipo_transporte_3': 2}},
                              {'term': {u'tipo_transporte_3': 4}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_2', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'parada_subida_3', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'fourth_transfer_is_end': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_4': u'auth_stop_code'}},
                              {'term': {u'n_etapas': 4}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_4', 'size': 5000}, 'aggs': {
                        u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}},
                u'first_transfer_is_end': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_1': u'auth_stop_code'}},
                              {'term': {u'n_etapas': 1}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_1', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'srv_2', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'third_transfer_is_end': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_3': u'auth_stop_code'}},
                              {'term': {u'n_etapas': 3}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_3', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'srv_4', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'third_transfer': {'filter': {'bool': {u'must_not': [{'term': {u'tipo_transporte_4': 2}},
                                                                      {'term': {u'tipo_transporte_4': 4}}],
                                                        u'must': [{'term': {
                                                            u'parada_bajada_3': u'auth_stop_code'}},
                                                            {'range': {u'n_etapas': {u'gt': 3}}}]}},
                                    'aggs': {u'route_from': {'terms': {'field': u'srv_3', 'size': 5000},
                                                             'aggs': {u'route_to': {
                                                                 'terms': {'field': u'srv_4',
                                                                           'size': 5000}, 'aggs': {
                                                                     u'expansion_factor': {'sum': {
                                                                         'field': u'factor_expansion'}}}}}}}},
                u'second_transfer_is_end': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_2': u'auth_stop_code'}},
                              {'term': {u'n_etapas': 2}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_2', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'srv_3', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}},
                u'first_transfer_to_subway': {'filter': {'bool': {
                    u'must': [{'term': {u'parada_bajada_1': u'auth_stop_code'}},
                              {'range': {u'n_etapas': {u'gt': 1}}}, {'term': {u'tipo_transporte_2': 2}},
                              {'term': {u'tipo_transporte_2': 4}}]}}, 'aggs': {
                    u'route_from': {'terms': {'field': u'srv_1', 'size': 5000}, 'aggs': {
                        u'route_to': {'terms': {'field': u'parada_subida_2', 'size': 5000}, 'aggs': {
                            u'expansion_factor': {'sum': {'field': u'factor_expansion'}}}}}}}}}}
        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)
