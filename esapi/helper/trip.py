# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import A
from elasticsearch_dsl.query import Q

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryDateRangeParametersDoesNotExist, ESQueryStagesEmpty, \
    ESQueryOriginZoneParameterDoesNotExist, ESQueryDestinationZoneParameterDoesNotExist, \
    ESQueryStopParameterDoesNotExist

import copy


class ESTripHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "trip"
        super(ESTripHelper, self).__init__(index_name)

        self.default_fields = ['tviaje', 'n_etapas', 'modos', 'factor_expansion', 'comuna_subida', 'comuna_bajada',
                               'zona_subida', 'zona_bajada']

    def _build_histogram_query(self, base_es_query):
        """
        Builds a elastic search query for the travels histogram
        It is based on the requested filtering options
        """

        def add_histogram(es_query, field, interval, b_min, b_max):
            es_query.aggs.bucket(field, 'histogram', field=field, interval=interval,
                                 min_doc_count=0, extended_bounds={'min': b_min, 'max': b_max}) \
                .metric('bin', 'sum', field='factor_expansion') \
                .pipeline('total', 'cumulative_sum', buckets_path='bin')

        # up to 120 min
        add_histogram(base_es_query, 'tviaje', '15', 0, 120)

        # at least from 1 to 5 etapas
        add_histogram(base_es_query, 'n_etapas', '1', 1, 5)

        # distances are this values right?
        add_histogram(base_es_query, 'distancia_ruta', '5000', 0, 30000)
        add_histogram(base_es_query, 'distancia_eucl', '5000', 0, 30000)

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return base_es_query[:0]

    def _build_indicators_query(self, base_es_query):
        base_es_query.aggs.metric('documentos', 'value_count', field='id')
        base_es_query.aggs.metric('viajes', 'sum', field='factor_expansion')
        base_es_query.aggs.metric('tviaje', 'stats', field='tviaje')
        base_es_query.aggs.metric('n_etapas', 'stats', field='n_etapas')
        base_es_query.aggs.metric('distancia_ruta', 'stats', field='distancia_ruta')
        base_es_query.aggs.metric('distancia_eucl', 'stats', field='distancia_eucl')

        # # limit fields
        # return base_es_query.source(self.default_fields)

        # return no hits!
        return base_es_query[:0]

    def ask_for_resume_data(self, start_date, end_date, day_types, periods, origin_zones, destination_zones):

        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        if origin_zones:
            es_query = es_query.filter('terms', zona_subida=origin_zones)

        if destination_zones:
            es_query = es_query.filter('terms', zona_bajada=destination_zones)

        es_query_dict = {
            'histogram': self._build_histogram_query(es_query),
            'indicators': self._build_indicators_query(es_query)
        }

        return es_query_dict

    def ask_for_available_days(self):
        return self.get_available_days('tiempo_subida')

    def ask_for_map_data(self, start_date, end_date, day_types, periods, sectors):
        """
        Builds a elastic search query for the travels map
        """
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_subida', size=1000)

        def add_remaining(query, sector, zones):
            query.aggs \
                .bucket(sector, A('filter', Q('terms', zona_bajada=zones))) \
                .bucket('by_zone', by_zone_agg) \
                .metric('tviaje', 'avg', field='tviaje') \
                .metric('n_etapas', 'avg', field='n_etapas') \
                .metric('distancia_ruta', 'avg', field='distancia_ruta') \
                .metric('distancia_eucl', 'avg', field='distancia_eucl')

        for key in sectors:
            add_remaining(es_query, key, sectors[key])

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return {
            'map': es_query[:0]
        }

    def ask_for_large_travel_data(self, start_date, end_date, day_types, periods, n_etapas):
        """
        Builds a elastic search query for the travels map
        It is based on the requested filtering options
        """
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        if n_etapas:
            if "5+" in n_etapas:
                n_etapas.remove("5+")
                es_query = es_query.query(Q('terms', n_etapas=n_etapas) | Q('range', n_etapas={'gte': 5}))
            else:
                es_query = es_query.filter('terms', n_etapas=n_etapas)
        else:
            raise ESQueryStagesEmpty()

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_subida', size=1000)

        # required stats
        es_query.aggs \
            .bucket('by_zone', by_zone_agg) \
            .metric('tviaje', 'avg', field='tviaje') \
            .metric('n_etapas', 'avg', field='n_etapas') \
            .metric('distancia_ruta', 'avg', field='distancia_ruta') \
            .metric('distancia_eucl', 'avg', field='distancia_eucl')

        # # limit fields
        # return es_query.source(self.default_fields)

        # return no hits!
        return {
            'large': es_query[:0]
        }

    def ask_for_from_to_map_data(self, start_date, end_date, day_types, periods, minutes, stages, modes):
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)
        if minutes:
            es_query = es_query.filter('terms', mediahora_subida=minutes)
        if stages:
            es_query = es_query.filter('terms', n_etapas=stages)
        # if modes:
        #    es_query = es_query.filter('terms', ?=modes)

        es_query = es_query[:0]

        def _query_by_zone(query, field):
            by_zone_agg = A('terms', field=field, size=1000)

            # required stats
            query.aggs \
                .bucket('by_zone', by_zone_agg) \
                .metric('tviaje', 'avg', field='tviaje') \
                .metric('n_etapas', 'avg', field='n_etapas') \
                .metric('distancia_ruta', 'avg', field='distancia_ruta') \
                .metric('distancia_eucl', 'avg', field='distancia_eucl')

        destination_es_query = copy.copy(es_query)
        _query_by_zone(es_query, 'zona_subida')
        _query_by_zone(destination_es_query, 'zona_bajada')

        return {
            'origin_zone': es_query,
            'destination_zone': destination_es_query
        }

    def ask_for_strategies_data(self, start_date, end_date, day_types, periods, minutes, origin_zones,
                                destination_zones):
        es_query = self.get_base_query()[:0]

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if not origin_zones:
            raise ESQueryOriginZoneParameterDoesNotExist()

        if not destination_zones:
            raise ESQueryDestinationZoneParameterDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)
        if minutes:
            es_query = es_query.filter('terms', mediahora_subida=minutes)
        if origin_zones:
            es_query = es_query.filter('terms', zona_subida=origin_zones)
        if destination_zones:
            es_query = es_query.filter('terms', zona_bajada=destination_zones)

        return es_query

    def ask_for_transfers_data(self, start_date, end_date, auth_stop_code, day_types, periods, half_hours):
        es_query = self.get_base_query()[:0]

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if not auth_stop_code:
            raise ESQueryStopParameterDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)
        if half_hours:
            es_query = es_query.filter('terms', mediahora_subida=half_hours)

        # TODO: hacer la agrupación

        return es_query
