# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryDateRangeParametersDoesNotExist


class ESTripHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "travel"
        super(ESTripHelper, self).__init__(index_name)

        self.default_fields = ['tviaje', 'n_etapas', 'factor_expansion', 'comuna_subida', 'comuna_bajada',
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
        print(base_es_query.to_dict())
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

    def ask_for_resume_data(self, start_date, end_date, day_types, periods, origin_zone, destination_zone):

        es_query = self.get_base_query()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter('range', tiempo_subida={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': 'America/Santiago'
        })

        if day_types:
            es_query = es_query.filter('terms', tipodia=day_types)

        if periods:
            es_query = es_query.filter('terms', periodo_subida=periods)

        if origin_zone and origin_zone >= 0:
            es_query = es_query.filter('term', zona_subida=origin_zone)

        if destination_zone and destination_zone >= 0:
            es_query = es_query.filter('term', zona_bajada=destination_zone)

        es_query_dict = {
            'histogram': self._build_histogram_query(es_query),
            'indicators': self._build_indicators_query(es_query)
        }

        return es_query_dict

    def ask_for_available_days(self):
        searches = {
            "days": self.get_histogram_query("tiempo_subida", interval="day", format="yyy-MM-dd")
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result
