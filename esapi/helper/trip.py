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
        file_extensions = ['trip']
        super(ESTripHelper, self).__init__(index_name, file_extensions)

    def _build_histogram_query(self, base_es_query):
        """
        Builds a elastic search query for the travels histogram
        It is based on the requested filtering options
        """

        def add_histogram(field, interval, b_min, b_max):
            base_es_query.aggs.bucket(field, 'histogram', field=field, interval=interval,
                                 min_doc_count=0, extended_bounds={'min': b_min, 'max': b_max}) \
                .metric('bin', 'sum', field='factor_expansion') \
                .pipeline('total', 'cumulative_sum', buckets_path='bin')

        # up to 120 min
        add_histogram('tviaje', '15', 0, 120)

        # at least from 1 to 5 stages
        add_histogram('n_etapas', '1', 1, 5)

        # distances are this values right?
        add_histogram('distancia_ruta', '5000', 0, 30000)
        add_histogram('distancia_eucl', '5000', 0, 30000)

        return base_es_query

    def _build_indicators_query(self, base_es_query):
        base_es_query.aggs.metric('documentos', 'value_count', field='id')
        base_es_query.aggs.metric('viajes', 'sum', field='factor_expansion')
        base_es_query.aggs.metric('tviaje', 'stats', field='tviaje')
        base_es_query.aggs.metric('n_etapas', 'stats', field='n_etapas')
        base_es_query.aggs.metric('distancia_ruta', 'stats', field='distancia_ruta')
        base_es_query.aggs.metric('distancia_eucl', 'stats', field='distancia_eucl')

        return base_es_query

    def get_base_resume_data_query(self, start_date, end_date, day_types, periods, origin_zones, destination_zones):
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

        return es_query

    def get_resume_data(self, start_date, end_date, day_types, periods, origin_zones, destination_zones):
        es_query = self.get_base_resume_data_query(start_date, end_date, day_types, periods, origin_zones,
                                                   destination_zones)[:0]
        histogram_es_query = copy.copy(es_query)
        return self._build_histogram_query(histogram_es_query), self._build_indicators_query(es_query)

    def get_available_days(self):
        return self._get_available_days('tiempo_subida')

    def get_base_map_data_query(self, start_date, end_date, day_types, periods, sectors):
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

        # TODO: esta restricción no existe sobre la consulta inicialmente, verificar que no cambia el resultado.
        """
        if sectors:
            destination_zones = []
            for _, zones in sectors.items():
                destination_zones += zones
            es_query = es_query.filter('terms', zona_bajada=[sectors[x] for x in sectors])
        """

        return es_query

    def get_map_data(self, start_date, end_date, day_types, periods, sectors):
        """
        Builds a elastic search query for the travels map
        """
        es_query = self.get_base_map_data_query(start_date, end_date, day_types, periods, sectors)[:0]

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field='zona_subida', size=1000)

        def add_remaining(query, sector, zones):
            query.aggs \
                .bucket(sector, A('filter', Q('terms', zona_bajada=zones))) \
                .bucket('by_zone', by_zone_agg) \
                .metric('tviaje', 'avg', field='tviaje') \
                .metric('n_etapas', 'avg', field='n_etapas') \
                .metric('distancia_ruta', 'avg', field='distancia_ruta') \
                .metric('distancia_eucl', 'avg', field='distancia_eucl') \
                .metric('expansion_factor', 'sum', field='factor_expansion')

        for key in sectors:
            add_remaining(es_query, key, sectors[key])

        es_query.aggs.metric('sum_expansion_factor', 'sum', field='factor_expansion')

        return es_query

    def get_base_large_travel_data_query(self, start_date, end_date, day_types, periods, n_etapas):
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

        return es_query

    def get_large_travel_data(self, start_date, end_date, day_types, periods, n_etapas, origin_or_destination):
        es_query = self.get_base_large_travel_data_query(start_date, end_date, day_types, periods, n_etapas)[:0]

        field_aggs_name = 'zona_subida'
        if origin_or_destination == 'destination':
            field_aggs_name = 'zona_bajada'

        # obs: by using size=1000, we assume there are less than '1000' zones
        by_zone_agg = A('terms', field=field_aggs_name, size=1000)

        # required stats
        es_query.aggs \
            .bucket('by_zone', by_zone_agg) \
            .metric('tviaje', 'avg', field='tviaje') \
            .metric('n_etapas', 'avg', field='n_etapas') \
            .metric('distancia_ruta', 'avg', field='distancia_ruta') \
            .metric('distancia_eucl', 'avg', field='distancia_eucl') \
            .metric('expansion_factor', 'sum', field='factor_expansion')
        # TODO: usar expansion_factor en el javascript para contar los viajes

        return es_query

    def get_base_from_to_map_data_query(self, start_date, end_date, day_types, periods, minutes, stages, modes):
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
        # TODO: uncomment this
        # if modes:
        #    es_query = es_query.filter('terms', ?=modes)

        return es_query

    def get_from_to_map_data(self, start_date, end_date, day_types, periods, minutes, stages, modes):
        es_query = self.get_base_from_to_map_data_query(start_date, end_date, day_types, periods, minutes, stages,
                                                        modes)[:0]

        def _query_by_zone(query, field):
            by_zone_agg = A('terms', field=field, size=1000)

            # required stats
            query.aggs \
                .bucket('by_zone', by_zone_agg) \
                .metric('tviaje', 'avg', field='tviaje') \
                .metric('n_etapas', 'avg', field='n_etapas') \
                .metric('distancia_ruta', 'avg', field='distancia_ruta') \
                .metric('distancia_eucl', 'avg', field='distancia_eucl') \
                .metric('expansion_factor', 'sum', field='factor_expansion')
            # TODO: en el javascript contar el expansion_factor, no el doc_count

        destination_es_query = copy.copy(es_query)
        _query_by_zone(es_query, 'zona_subida')
        _query_by_zone(destination_es_query, 'zona_bajada')

        # origin zone, destination zone
        return es_query, destination_es_query

    def get_base_strategies_data_query(self, start_date, end_date, day_types, periods, minutes, origin_zones,
                                       destination_zones):
        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()
        """
        if not origin_zones:
            raise ESQueryOriginZoneParameterDoesNotExist()

        if not destination_zones:
            raise ESQueryDestinationZoneParameterDoesNotExist()
        """
        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        # TODO: removed this
        origin_zones = range(0, 50)
        destination_zones = range(0, 100)
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

    def get_strategies_data(self, start_date, end_date, day_types, periods, minutes, origin_zones,
                            destination_zones):
        es_query = self.get_base_strategies_data_query(start_date, end_date, day_types, periods, minutes, origin_zones,
                                                       destination_zones)[:0]

        first_transport_mode = A('terms', field='srv_1', size=2000)
        second_transport_mode = A('terms', field='srv_2', size=2000)
        third_transport_mode = A('terms', field='srv_3', size=2000)
        fourth_transport_mode = A('terms', field='srv_4', size=2000)

        es_query.aggs.bucket('strategies', first_transport_mode).bucket('second', second_transport_mode). \
            bucket('third', third_transport_mode).bucket('fourth', fourth_transport_mode)
        es_query.aggs['strategies']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['tipo_transporte_1'])
        es_query.aggs['strategies']['second']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['tipo_transporte_2'])
        es_query.aggs['strategies']['second']['third']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['tipo_transporte_3'])
        es_query.aggs['strategies']['second']['third']['fourth']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['tipo_transporte_4']). \
            metric('expansion_factor', 'sum', field='factor_expansion')

        return es_query

    def get_base_transfers_data_query(self, start_date, end_date, auth_stop_code, day_types, periods, half_hours):
        es_query = self.get_base_query()

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

        landing_stop_in_first_stage = Q('term', parada_bajada_1=auth_stop_code)
        landing_stop_in_second_stage = Q('term', parada_bajada_2=auth_stop_code)
        landing_stop_in_third_stage = Q('term', parada_bajada_3=auth_stop_code)
        landing_stop_in_fourth_stage = Q('term', parada_bajada_4=auth_stop_code)
        es_query = es_query.filter(
            landing_stop_in_first_stage | landing_stop_in_second_stage | landing_stop_in_third_stage | landing_stop_in_fourth_stage)

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        if periods:
            period_in_first_stage = Q('terms', periodo_bajada_1=periods)
            period_in_second_stage = Q('terms', periodo_bajada_2=periods)
            period_in_third_stage = Q('terms', periodo_bajada_3=periods)
            period_in_fourth_stage = Q('terms', periodo_bajada_4=periods)
            es_query = es_query.filter(
                period_in_first_stage | period_in_second_stage | period_in_third_stage | period_in_fourth_stage)
        if half_hours:
            half_hour_in_first_stage = Q('terms', mediahora_bajada_1=half_hours)
            half_hour_in_second_stage = Q('terms', mediahora_bajada_2=half_hours)
            half_hour_in_third_stage = Q('terms', mediahora_bajada_3=half_hours)
            half_hour_in_fourth_stage = Q('terms', mediahora_bajada_4=half_hours)
            es_query = es_query.filter(
                half_hour_in_first_stage | half_hour_in_second_stage | half_hour_in_third_stage | half_hour_in_fourth_stage)

        return es_query

    def get_transfers_data(self, start_date, end_date, auth_stop_code, day_types, periods, half_hours):

        es_query = self.get_base_transfers_data_query(start_date, end_date, auth_stop_code, day_types, periods,
                                                      half_hours)

        def add_aggregation(bucket_name, stop_name, additonal_conditions, stage_route_init, stage_route_end):
            conditions = [{'term': {}}] + additonal_conditions
            conditions[0]['term'][stop_name] = auth_stop_code
            aggregation = A('filter', Q({'bool': {'must': conditions}}))

            transfer_bucket = es_query.aggs.bucket(bucket_name, aggregation)
            transfer_bucket.bucket('route_from', 'terms', field=stage_route_init, size=5000)
            if stage_route_end is None:
                transfer_bucket.aggs['route_from'].metric('expansion_factor', 'sum', field='factor_expansion')
            else:
                transfer_bucket.aggs['route_from'].bucket('route_to', 'terms', field=stage_route_end, size=5000)
                transfer_bucket.aggs['route_from']['route_to'].metric('expansion_factor', 'sum',
                                                                      field='factor_expansion')

            return transfer_bucket

        add_aggregation('first_transfer', 'parada_bajada_1', [{'range': {'n_etapas': {'gt': 1}}}], 'srv_1', 'srv_2')
        add_aggregation('second_transfer', 'parada_bajada_2', [{'range': {'n_etapas': {'gt': 2}}}], 'srv_2', 'srv_3')
        add_aggregation('third_transfer', 'parada_bajada_3', [{'range': {'n_etapas': {'gt': 3}}}], 'srv_3', 'srv_4')

        add_aggregation('first_transfer_is_end', 'parada_bajada_1', [{'term': {'n_etapas': 1}}], 'srv_1', 'srv_2')
        add_aggregation('second_transfer_is_end', 'parada_bajada_2', [{'term': {'n_etapas': 2}}], 'srv_2', 'srv_3')
        add_aggregation('third_transfer_is_end', 'parada_bajada_3', [{'term': {'n_etapas': 3}}], 'srv_3', 'srv_4')
        add_aggregation('fourth_transfer_is_end', 'parada_bajada_4', [{'term': {'n_etapas': 4}}], 'srv_4', None)

        subway = [{'term': {'n_etapas': 1}}, {}]
        # add_aggregation('first_transfer_is_end', 'parada_bajada_1', , 'srv_1', 'srv_2')
        return es_query
