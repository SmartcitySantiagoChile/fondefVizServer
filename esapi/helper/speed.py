# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
from elasticsearch_dsl import A

from localinfo.helper import get_operator_list_for_select_input

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryResultEmpty, ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryOperatorParameterDoesNotExist


class ESSpeedHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "speed"
        super(ESSpeedHelper, self).__init__(index_name)

    def get_route_list(self, valid_operator_list):

        es_query = self.get_base_query()[:0]
        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        searches = {
            'routes': self.get_unique_list_query('route', size=5000, query=es_query)
        }
        result = self.make_multisearch_query_for_aggs(searches)['routes']

        return result

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('date', valid_operator_list)

    def get_available_routes(self, valid_operator_list):
        """
        This is used in data filter panel
        :param valid_operator_list: operators which user can ask
        :return: dicts with available routes for user
        """
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        aggs = A('terms', field="authRouteCode", size=5000)
        es_query.aggs.bucket('route', aggs)
        es_query.aggs['route']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['operator', 'userRouteCode'])

        operator_list = get_operator_list_for_select_input(filter=valid_operator_list)

        result = defaultdict(lambda: defaultdict(list))

        for hit in es_query.execute().aggregations.route.buckets:
            data = hit.to_dict()
            auth_route = data['key']
            operator_id = data['additionalInfo']['hits']['hits'][0]['_source']['operator']
            user_route = data['additionalInfo']['hits']['hits'][0]['_source']['userRouteCode']

            result[operator_id][user_route].append(auth_route)

        return result, operator_list

    def get_base_speed_data_query(self, auth_route, day_type, start_date, end_date, valid_operator_list):
        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        if auth_route:
            es_query = es_query.filter("term", authRouteCode=auth_route)
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        es_query = es_query.filter("range", date={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })

        return es_query

    def get_speed_data(self, auth_route, day_type, start_date, end_date, valid_operator_list):
        es_query = self.get_base_speed_data_query(auth_route, day_type, start_date, end_date, valid_operator_list)[:0]

        aggs2 = A('terms', field='section', size=1000)
        aggs1 = A('terms', field='periodId', size=1000)
        aggs2.metric('distance', 'sum', field='totalDistance')
        aggs2.metric('time', 'sum', field='totalTime')
        aggs2.metric('n_obs', 'sum', field='nObs')
        es_query.aggs.bucket('periods', aggs1).bucket('sections', aggs2)

        # transform data
        d_data = {}
        for period in es_query.execute().aggregations.periods.buckets:
            key_period = period.key
            for section in period.sections.buckets:
                key_section = section.key
                d_data[(key_section, key_period)] = (
                    -1 if section.time.value == 0 else 3.6 * section.distance.value / section.time.value,
                    section.n_obs.value)

        if len(d_data.keys()) == 0:
            raise ESQueryResultEmpty()

        return d_data

    def get_base_ranking_data_query(self, start_date, end_date, hour_period_from, hour_period_to, day_type,
                                    valid_operator_list, route_list=None):
        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        es_query = es_query.filter('range', date={
            "gte": start_date,
            "lte": end_date,
            "format": "yyyy-MM-dd"
        })
        es_query = es_query.filter('range', periodId={
            "gte": hour_period_from,
            "lte": hour_period_to
        })

        if route_list is not None:
            es_query = es_query.filter('terms', authRouteCode=route_list)

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        return es_query

    def get_ranking_data(self, start_date, end_date, hour_period_from, hour_period_to, day_type, valid_operator_list):

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        data = []
        # chunks of routes to make queries
        chunks_number = 6
        routes = self.get_route_list(valid_operator_list)
        indices = [int(i * len(routes) / chunks_number) for i in range(chunks_number + 1)]
        chunks = [routes[i:j] for i, j in zip(indices[:-1], indices[1:])]

        for chunk in chunks:
            es_query = self.get_base_ranking_data_query(start_date, end_date, hour_period_from, hour_period_to,
                                                        day_type, valid_operator_list, chunk)[:0]

            aggs0 = A('terms', field='merged', size=100000000)
            aggs0.metric('n_obs', 'sum', field='nObs')
            aggs0.metric('distance', 'sum', field='totalDistance')
            aggs0.metric('time', 'sum', field='totalTime')
            aggs0.metric('speed', 'bucket_script', script='params.d / params.t',
                         buckets_path={'d': 'distance', 't': 'time'})
            es_query.aggs.bucket('tuples', aggs0)

            for tup in es_query.execute().aggregations.tuples.buckets:
                tha_key = tup.key
                tha_value = 3.6 * tup.speed.value
                # if tha_value < 15:
                sep_key = tha_key.split('-')
                data.append({
                    'route': sep_key[0],
                    'section': int(sep_key[1]),
                    'period': int(sep_key[2]),
                    'n_obs': tup.n_obs.value,
                    'distance': tup.distance.value,
                    'time': tup.time.value,
                    'speed': tha_value
                })

        data.sort(key=lambda x: float(x['speed']))

        if len(data) == 0:
            raise ESQueryResultEmpty()

        return data

    def get_base_detail_ranking_data_query(self, route, start_date, end_date, period, day_type, valid_operator_list):
        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        es_query = es_query.filter('term', authRouteCode=route)
        es_query = es_query.filter('range', date={
            "gte": start_date,
            "lte": end_date, "format": "yyyy-MM-dd"})
        es_query = es_query.filter('term', periodId=int(period))
        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        return es_query

    def get_detail_ranking_data(self, route, start_date, end_date, period, day_type, valid_operator_list):
        es_query = self.get_base_detail_ranking_data_query(route, start_date, end_date, period, day_type,
                                                           valid_operator_list)[:0]

        aggs0 = A('terms', field='section', size=200)
        aggs0.metric('n_obs', 'sum', field='nObs')
        aggs0.metric('distance', 'sum', field='totalDistance')
        aggs0.metric('time', 'sum', field='totalTime')
        aggs0.metric('speed', 'bucket_script', script='params.d / params.t',
                     buckets_path={'d': 'distance', 't': 'time'})
        es_query.aggs.bucket('sections', aggs0)

        return es_query

    def get_base_variation_speed_query(self, start_date, end_date, day_type, user_route, operator, valid_operator_list):
        es_query = self.get_base_query()
        es_query = es_query.filter('range', date={
            "gte": start_date,
            "lte": end_date,
            "format": "yyyy-MM-dd"
        })
        if valid_operator_list and operator in valid_operator_list:
            es_query = es_query.filter('terms', operator=operator)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        if user_route:
            es_query = es_query.filter('term', userRouteCode=user_route)
        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)

        return es_query

    def get_speed_variation_data(self, start_date, end_date, day_type, user_route, operator, valid_operator_list):
        """
        it calculates speed variation for end_date taking account the speed calculated from start_date to end_date - 1

        :param start_date:
        :param end_date:
        :param day_type:
        :param user_route:
        :param operator:
        :param valid_operator_list:
        :return:
        """
        es_query = self.get_base_variation_speed_query(start_date, end_date, day_type, user_route, operator,
                                                       valid_operator_list)[:0]

        aggs0 = A('terms', field='route', size=2000)
        aggs1 = A('terms', field='periodId', size=50)
        aggs2 = A('range', field='date', format='yyyy-MM-dd', ranges=[
            {'to': end_date},
            {'from': end_date}
        ])

        aggs2.metric('distance', 'sum', field='totalDistance')
        aggs2.metric('time', 'sum', field='totalTime')
        aggs2.metric('n_obs', 'sum', field='nObs')
        aggs2.metric('stats', 'extended_stats', field='speed')
        aggs2.metric('speed', 'bucket_script', script='params.d / params.t',
                     buckets_path={'d': 'distance', 't': 'time'})
        es_query.aggs.bucket('routes', aggs0).bucket('periods', aggs1).bucket('days', aggs2)

        # print(str(esQuery.to_dict()).replace('u\'', '"').replace('\'', '"'))
        return es_query
