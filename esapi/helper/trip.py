import copy
import itertools
from functools import reduce

from elasticsearch_dsl import A
from elasticsearch_dsl.query import Q

from esapi.errors import ESQueryDateRangeParametersDoesNotExist, ESQueryStagesEmpty, \
    ESQueryOriginZoneParameterDoesNotExist, ESQueryDestinationZoneParameterDoesNotExist, \
    ESQueryStopParameterDoesNotExist, ESQueryTooManyOriginZonesError, ESQueryTooManyDestinationZonesError
from esapi.helper.basehelper import ElasticSearchHelper


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
        base_es_query.aggs.metric('documentos', 'value_count', field='n_etapas')
        base_es_query.aggs.metric('viajes', 'sum', field='factor_expansion')
        base_es_query.aggs.metric('tviaje', 'stats', field='tviaje')
        base_es_query.aggs.metric('n_etapas', 'stats', field='n_etapas')
        base_es_query.aggs.metric('distancia_ruta', 'stats', field='distancia_ruta')
        base_es_query.aggs.metric('distancia_eucl', 'stats', field='distancia_eucl')
        return base_es_query

    def get_base_resume_data_query(self, dates, day_types, periods, origin_zones, destination_zones):
        es_query = self.get_base_query()

        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        if origin_zones:
            es_query = es_query.filter('terms', zona_subida=origin_zones)

        if destination_zones:
            es_query = es_query.filter('terms', zona_bajada=destination_zones)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)

        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        return es_query

    def get_resume_data(self, dates, day_types, periods, origin_zones, destination_zones):
        es_query = self.get_base_resume_data_query(dates, day_types, periods, origin_zones,
                                                   destination_zones)[:0]
        histogram_es_query = copy.copy(es_query)
        return self._build_histogram_query(histogram_es_query), self._build_indicators_query(es_query)

    def get_available_days(self):
        return self._get_available_days('tiempo_subida')

    def get_base_map_data_query(self, dates, day_types, periods, sectors):
        es_query = self.get_base_query()

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
        # TODO: esta restricción no existe sobre la consulta inicialmente, verificar que no cambia el resultado.
        """
        if sectors:
            destination_zones = []
            for _, zones in sectors.items():
                destination_zones += zones
            es_query = es_query.filter('terms', zona_bajada=[sectors[x] for x in sectors])
        """

        return es_query

    def get_map_data(self, dates, day_types, periods, sectors):
        """
        Builds a elastic search query for the travels map
        """
        es_query = self.get_base_map_data_query(dates, day_types, periods, sectors)[:0]

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

    def get_base_large_travel_data_query(self, dates, day_types, periods, n_etapas):
        es_query = self.get_base_query()
        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

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

    def get_large_travel_data(self, dates, day_types, periods, n_etapas, origin_or_destination):
        es_query = self.get_base_large_travel_data_query(dates, day_types, periods, n_etapas)[:0]

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

        es_query.aggs.metric('sum_expansion_factor', 'sum', field='factor_expansion')

        return es_query

    def get_base_from_to_map_data_query(self, dates, day_types, periods, minutes, stages, modes,
                                        origin_zones, destination_zones, routes):
        es_query = self.get_base_query()

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)
        if minutes:
            es_query = es_query.filter('terms', mediahora_subida=minutes)
        if stages:
            es_query = es_query.filter('terms', n_etapas=stages)
        if modes:
            es_query = es_query.filter('terms', modos=modes)
        if origin_zones:
            es_query = es_query.filter('terms', zona_subida=origin_zones)
        if destination_zones:
            es_query = es_query.filter('terms', zona_bajada=destination_zones)
        if routes:
            routes_filter = []
            if not stages:
                stages = ['1', '2', '3', '4']
            for stage in stages:
                srv = dict()
                srv['srv_{0}'.format(stage)] = routes
                filter_q = Q('terms', **srv)
                routes_filter.append(filter_q)
            routes_filter = reduce((lambda x, y: x | y), routes_filter)
            es_query = es_query.query('bool', filter=[routes_filter])

        return es_query

    def get_from_to_map_data(self, dates, day_types, periods, minutes, stages, modes, origin_zones,
                             destination_zones, routes):
        es_query = self.get_base_from_to_map_data_query(dates, day_types, periods, minutes, stages,
                                                        modes, origin_zones, destination_zones, routes)[:0]

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

        destination_es_query = copy.copy(es_query)
        _query_by_zone(es_query, 'zona_subida')
        _query_by_zone(destination_es_query, 'zona_bajada')
        es_query.aggs.metric('expansion_factor', 'sum', field='factor_expansion')

        # origin zone, destination zone
        return es_query, destination_es_query

    def get_base_strategies_data_query(self, dates, day_types, periods, minutes, origin_zones,
                                       destination_zones, routes):
        if not dates or not isinstance(dates[0], list) or not dates[0]:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = self.get_base_query()
        origin_zone_limit = 50
        destination_zone_limit = 50
        if not origin_zones:
            raise ESQueryOriginZoneParameterDoesNotExist()

        if len(origin_zones) > origin_zone_limit:
            raise ESQueryTooManyOriginZonesError(origin_zone_limit)

        if not destination_zones:
            raise ESQueryDestinationZoneParameterDoesNotExist()

        if len(destination_zones) > destination_zone_limit:
            raise ESQueryTooManyDestinationZonesError(destination_zone_limit)

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

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

        if routes:
            routes_filter = [Q('terms', srv_1=routes), Q('terms', srv_2=routes), Q('terms', srv_3=routes),
                             Q('terms', srv_4=routes)]
            routes_filter = reduce((lambda x, y: x | y), routes_filter)
            es_query = es_query.query('bool', filter=[routes_filter])

        return es_query

    def get_strategies_data(self, dates, day_types, periods, minutes, origin_zones,
                            destination_zones, routes):
        es_query = self.get_base_strategies_data_query(dates, day_types, periods, minutes, origin_zones,
                                                       destination_zones, routes)[:0]
        query_filter = Q({'bool': {'must_not': {'bool': {
            'should': [{'terms': {'tipo_transporte_1': [2, 4]}}, {'terms': {'tipo_transporte_2': [2, 4]}},
                       {'terms': {'tipo_transporte_3': [2, 4]}}, {'terms': {'tipo_transporte_4': [2, 4]}}]}}}})
        first_transport_mode = A('terms', field='srv_1', size=2000)
        second_transport_mode = A('terms', field='srv_2', size=2000)
        third_transport_mode = A('terms', field='srv_3', size=2000)
        fourth_transport_mode = A('terms', field='srv_4', size=2000)

        es_query.aggs.bucket('strategies_without_metro_or_metrotren', A('filter', query_filter)). \
            bucket('first', first_transport_mode).bucket('second', second_transport_mode). \
            bucket('third', third_transport_mode).bucket('fourth', fourth_transport_mode). \
            metric('expansion_factor', 'sum', field='factor_expansion')

        # total
        es_query.aggs.metric('expansion_factor', 'sum', field='factor_expansion')

        FIRST_MODE = 'first_mode'
        FIRST_START_STATION = 'first_start_station'
        FIRST_END_STATION = 'first_end_station'
        SECOND_MODE = 'second_mode'
        SECOND_START_STATION = 'second_start_station'
        SECOND_END_STATION = 'second_end_station'
        THIRD_MODE = 'third_mode'
        THIRD_START_STATION = 'third_start_station'
        THIRD_END_STATION = 'third_end_station'
        FOURTH_MODE = 'fourth_mode'
        FOURTH_START_STATION = 'fourth_start_station'
        FOURTH_END_STATION = 'fourth_end_station'
        structure = {
            FIRST_MODE: ['first', A('terms', field='srv_1', size=2000)],
            FIRST_START_STATION: ['start_station_1', A('terms', field='parada_subida_1', size=5000)],
            FIRST_END_STATION: ['end_station_1', A('terms', field='parada_bajada_1', size=5000)],
            SECOND_MODE: ['second', A('terms', field='srv_2', size=2000)],
            SECOND_START_STATION: ['start_station_2', A('terms', field='parada_subida_2', size=5000)],
            SECOND_END_STATION: ['end_station_2', A('terms', field='parada_bajada_2', size=5000)],
            THIRD_MODE: ['third', A('terms', field='srv_3', size=2000)],
            THIRD_START_STATION: ['start_station_3', A('terms', field='parada_subida_3', size=5000)],
            THIRD_END_STATION: ['end_station_3', A('terms', field='parada_bajada_3', size=5000)],
            FOURTH_MODE: ['fourth', A('terms', field='srv_4', size=2000)],
            FOURTH_START_STATION: ['start_station_4', A('terms', field='parada_subida_4', size=5000)],
            FOURTH_END_STATION: ['end_station_4', A('terms', field='parada_bajada_4', size=5000)],
        }

        def build_aggregation(bucket_name, filter_criteria, nested_order):
            strategies_with_metro_or_metrotren = A('filter', Q(filter_criteria))
            bucket = es_query.aggs.bucket(bucket_name, strategies_with_metro_or_metrotren)

            for group in nested_order:
                bucket_name = structure[group][0]
                aggregation = copy.deepcopy(structure[group][1])
                bucket = bucket.bucket(bucket_name, aggregation)
            bucket.metric('expansion_factor', 'sum', field='factor_expansion')

        elements = [
            {'terms': {'tipo_transporte_1': [2, 4]}},
            {'terms': {'tipo_transporte_2': [2, 4]}},
            {'terms': {'tipo_transporte_3': [2, 4]}},
            {'terms': {'tipo_transporte_4': [2, 4]}},
        ]

        filters = list(itertools.combinations(elements, 1)) + list(itertools.combinations(elements, 2)) + list(
            itertools.combinations(elements, 3)) + list(itertools.combinations(elements, 4))

        names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        queries = [
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_MODE, THIRD_MODE, FOURTH_MODE],
            [FIRST_MODE, SECOND_START_STATION, SECOND_END_STATION, THIRD_MODE, FOURTH_MODE],
            [FIRST_MODE, SECOND_MODE, THIRD_START_STATION, THIRD_END_STATION, FOURTH_MODE],
            [FIRST_MODE, SECOND_MODE, THIRD_MODE, FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_START_STATION, SECOND_END_STATION, THIRD_MODE, FOURTH_MODE],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_MODE, THIRD_START_STATION, THIRD_END_STATION, FOURTH_MODE],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_MODE, THIRD_MODE, FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_MODE, SECOND_START_STATION, SECOND_END_STATION, THIRD_START_STATION, THIRD_END_STATION, FOURTH_MODE],
            [FIRST_MODE, SECOND_START_STATION, SECOND_END_STATION, THIRD_MODE, FOURTH_START_STATION,
             FOURTH_END_STATION],
            [FIRST_MODE, SECOND_MODE, THIRD_START_STATION, THIRD_END_STATION, FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_START_STATION, SECOND_END_STATION, THIRD_START_STATION,
             THIRD_END_STATION, FOURTH_MODE],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_START_STATION, SECOND_END_STATION, THIRD_MODE,
             FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_MODE, THIRD_START_STATION, THIRD_END_STATION,
             FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_MODE, SECOND_START_STATION, SECOND_END_STATION, THIRD_START_STATION, THIRD_END_STATION,
             FOURTH_START_STATION, FOURTH_END_STATION],
            [FIRST_START_STATION, FIRST_END_STATION, SECOND_START_STATION, SECOND_END_STATION, THIRD_START_STATION,
             THIRD_END_STATION, FOURTH_START_STATION, FOURTH_END_STATION]
        ]
        for name, data_filter, query in zip(names, filters, queries):
            data_filter = [x for x in data_filter]
            build_aggregation(name, {'bool': {'filter': data_filter}}, query)

        return es_query

    def get_base_transfers_data_query(self, dates, auth_stop_code, day_types, periods, half_hours):
        es_query = self.get_base_query()
        if not auth_stop_code:
            raise ESQueryStopParameterDoesNotExist()
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
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

    def get_transfers_data(self, dates, auth_stop_code, day_types, periods, half_hours):

        es_query = self.get_base_transfers_data_query(dates, auth_stop_code, day_types, periods,
                                                      half_hours)

        def add_aggregation(bucket_name, stop_name, additional_conditions, stage_route_init, stage_route_end,
                            not_conditions=None):
            conditions = [{'term': {}}]
            conditions[0]['term'][stop_name] = auth_stop_code
            conditions += additional_conditions
            not_conditions = [] if not_conditions is None else not_conditions
            aggregation = A('filter', Q({'bool': {'must': conditions, 'must_not': not_conditions}}))

            transfer_bucket = es_query.aggs.bucket(bucket_name, aggregation)
            transfer_bucket.bucket('route_from', 'terms', field=stage_route_init, size=5000)
            if stage_route_end is None:
                transfer_bucket.aggs['route_from'].metric('expansion_factor', 'sum', field='factor_expansion')
            else:
                transfer_bucket.aggs['route_from'].bucket('route_to', 'terms', field=stage_route_end, size=5000)
                transfer_bucket.aggs['route_from']['route_to'].metric('expansion_factor', 'sum',
                                                                      field='factor_expansion')

            return transfer_bucket

        first_condition = [{'range': {'n_etapas': {'gt': 1}}}]
        second_condition = [{'range': {'n_etapas': {'gt': 2}}}]
        third_condition = [{'range': {'n_etapas': {'gt': 3}}}]

        first_not_condition = [{'term': {'tipo_transporte_2': 2}}, {'term': {'tipo_transporte_2': 4}}]
        second_not_condition = [{'term': {'tipo_transporte_3': 2}}, {'term': {'tipo_transporte_3': 4}}]
        third_not_condition = [{'term': {'tipo_transporte_4': 2}}, {'term': {'tipo_transporte_4': 4}}]

        add_aggregation('first_transfer', 'parada_bajada_1', first_condition, 'srv_1', 'srv_2')
        add_aggregation('second_transfer', 'parada_bajada_2', second_condition, 'srv_2', 'srv_3')
        add_aggregation('third_transfer', 'parada_bajada_3', third_condition, 'srv_3', 'srv_4')

        add_aggregation('first_transfer_is_end', 'parada_bajada_1', [{'term': {'n_etapas': 1}}], 'srv_1', 'srv_2')
        add_aggregation('second_transfer_is_end', 'parada_bajada_2', [{'term': {'n_etapas': 2}}], 'srv_2', 'srv_3')
        add_aggregation('third_transfer_is_end', 'parada_bajada_3', [{'term': {'n_etapas': 3}}], 'srv_3', 'srv_4')
        add_aggregation('fourth_transfer_is_end', 'parada_bajada_4', [{'term': {'n_etapas': 4}}], 'srv_4', None)

        add_aggregation('first_transfer_to_subway', 'parada_bajada_1', first_condition + first_not_condition, 'srv_1',
                        'parada_subida_2')
        add_aggregation('second_transfer_to_subway', 'parada_bajada_2', second_condition + second_not_condition,
                        'srv_2', 'parada_subida_3')
        add_aggregation('third_transfer_to_subway', 'parada_bajada_3', third_condition + third_not_condition, 'srv_3',
                        'parada_subida_4')

        return es_query

    def get_all_time_periods(self):
        """
        Make a query that get all time periods in index
        Returns: ES query
        """
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query_bucket = es_query.aggs.bucket('time_periods_per_file', 'terms', field='path', size=5000)
        es_query_bucket.bucket('time_periods_0', 'terms', field='periodo_subida')
        es_query_bucket.bucket('time_periods_1', 'terms', field='periodo_bajada')
        es_query_bucket.bucket('time_periods_2', 'terms', field='periodo_bajada_1')
        es_query_bucket.bucket('time_periods_3', 'terms', field='periodo_bajada_2')
        es_query_bucket.bucket('time_periods_4', 'terms', field='periodo_bajada_3')
        es_query_bucket.bucket('time_periods_5', 'terms', field='periodo_bajada_4')
        return es_query

    def get_post_products_base_query(self, dates, day_types):
        es_query = self.get_base_query()
        es_query = es_query[:0]

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q('range', tiempo_subida={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)
        return es_query

    def get_post_products_trip_between_zone_data_query(self, dates, day_types):
        es_query = self.get_post_products_base_query(dates, day_types)
        es_query.aggs.bucket('dayType', 'terms', field='tipodia', size=4). \
            bucket('startCommune', 'terms', field='comuna_subida', size=48). \
            bucket('endCommune', 'terms', field='comuna_bajada', size=13000). \
            bucket('transportModes', 'terms', field='modos', size=6). \
            bucket('halfHourInBoardingTime', 'terms', field='mediahora_subida', size=48). \
            metric('tripNumber', 'sum', field='factor_expansion'). \
            metric('expandedTime', 'sum', script="doc['tviaje'].value * doc['factor_expansion'].value"). \
            metric('expandedDistance', 'sum', script="doc['distancia_ruta'].value * doc['factor_expansion'].value"). \
            metric('expandedStages', 'sum', script="doc['n_etapas'].value * doc['factor_expansion'].value")
        return es_query

    def get_post_products_boarding_and_alighting_data_query(self, dates, day_types):
        es_query = self.get_post_products_base_query(dates, day_types)

        day_type_bucket = es_query.aggs.bucket('dayType', 'terms', field='tipodia', size=4)
        day_type_bucket.bucket('boardingStopCommune', 'terms', field='comuna_subida', size=48). \
            bucket('authStopCode', 'terms', field='paradero_subida', size=13000). \
            bucket('transportModes', 'terms', field='modos', size=6). \
            bucket('authRouteCode', 'terms', field='srv_1', size=5000). \
            bucket('halfHourInBoardingTime', 'terms', field='mediahora_subida', size=48). \
            metric('expandedBoarding', 'sum', field='factor_expansion')

        day_type_bucket.bucket('alightingStopCommune', 'terms', field='comuna_bajada', size=48). \
            bucket('authStopCode', 'terms', field='paradero_bajada', size=13000). \
            bucket('transportModes', 'terms', field='modos', size=6). \
            bucket('authRouteCode', 'terms', field='servicio_bajada', size=5000). \
            bucket('halfHourInAlightingTime', 'terms', field='mediahora_bajada', size=48). \
            metric('expandedAlighting', 'sum', field='factor_expansion')

        return es_query
