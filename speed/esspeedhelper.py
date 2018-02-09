# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import A

from bowerapp.eshelper.eshelper import ElasticSearchHelper

from errors import ESQueryResultEmpty

from localinfo.models import Operator


class ESSpeedHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "speed"
        super(ESSpeedHelper, self).__init__(index_name)

    def get_base_params(self):
        es_day_type_query = self.get_unique_list_query("dayType", size=10)
        result = {
            "day_types": es_day_type_query
        }

        return result

    def get_route_list(self):
        searches = {
            "routes": self.get_unique_list_query("route", size=5000)
        }
        result = self.make_multisearch_query_for_aggs(searches)["routes"]

        return result

    def ask_for_available_days(self):
        searches = {
            "days": self.get_histogram_query("date", interval="day", format="yyy-MM-dd")
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result

    def ask_for_available_routes(self):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        aggs = A('terms', field="route", size=5000)
        es_query.aggs.bucket('route', aggs)
        # TODO: remove this when data source is updated
        # es_query.aggs['route']. \
        #    metric('additionalInfo', 'top_hits', size=1, _source=['operator', 'userRoute'])

        operator_list = [{"id": op[0], "text": op[1]} for op in Operator.objects.values_list('esId', 'name')]

        result = defaultdict(lambda: defaultdict(list))
        for hit in es_query.execute().aggregations.route.buckets:
            data = hit.to_dict()
            authRoute = data['key']
            # TODO: remove this when data source is updated
            # operatorId = data['additionalInfo']['hits']['hits'][0]['_source']['operator']
            # userRoute = data['additionalInfo']['hits']['hits'][0]['_source']['userRoute']

            # TODO: remove this
            operatorId = 1
            userRoute = "506I"
            result[operatorId][userRoute].append(authRoute)

        return result, operator_list

    def get_speed_data(self, auth_route, day_type, start_date, end_date):

        esQuery = self.get_base_query()
        esQuery = esQuery.filter("term", route=auth_route)
        if day_type:
            esQuery = esQuery.filter('terms', dayType=day_type)

        esQuery = esQuery.filter("range", date={'gte': start_date, 'lte': end_date, 'format': 'yyyy-MM-dd'})
        aggs2 = A('terms', field='section', size=1000)
        aggs1 = A('terms', field='periodId', size=1000)
        aggs2.metric('distance', 'sum', field='totalDistance')
        aggs2.metric('time', 'sum', field='totalTime')
        aggs2.metric('n_obs', 'sum', field='nObs')
        esQuery.aggs.bucket('periods', aggs1).bucket('sections', aggs2)

        result = esQuery.execute()

        d_data = {}
        for period in result.aggregations.periods.buckets:
            key_period = period.key
            for section in period.sections.buckets:
                key_section = section.key
                d_data[(key_section, key_period)] = (
                    -1 if section.time.value == 0 else 3.6 * section.distance.value / section.time.value,
                    section.n_obs.value)

        if len(d_data.keys()) == 0:
            raise ESQueryResultEmpty

        return d_data

    def get_ranking_data(self, start_date, end_date, hour_period_from, hour_period_to, day_type):

        data = []

        # chunks of routes to make queries
        chunks_number = 6
        routes = self.get_route_list()
        indices = [int(i * len(routes) / chunks_number) for i in range(chunks_number + 1)]
        chunks = [routes[i:j] for i, j in zip(indices[:-1], indices[1:])]

        for chunk in chunks:
            esQuery = self.get_base_query()
            esQuery = esQuery.filter('terms', route=chunk)
            esQuery = esQuery.filter('range', date={
                "gte": start_date,
                "lte": end_date,
                "format": "yyyy-MM-dd"})
            esQuery = esQuery.filter('range', periodId={
                "gte": hour_period_from,
                "lte": hour_period_to})
            if day_type:
                esQuery = esQuery.filter('terms', dayType=day_type)

            aggs0 = A('terms', field='merged', size=100000000)
            aggs0.metric('n_obs', 'sum', field='nObs')
            aggs0.metric('distance', 'sum', field='totalDistance')
            aggs0.metric('time', 'sum', field='totalTime')
            aggs0.metric('speed', 'bucket_script', script='params.d / params.t',
                         buckets_path={'d': 'distance', 't': 'time'})
            esQuery.aggs.bucket('tuples', aggs0)

            for tup in esQuery.execute().aggregations.tuples.buckets:
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
            raise ESQueryResultEmpty

        return data

    def get_detail_ranking_data(self, route, start_date, end_date, period, day_type, limits):

        esQuery = self.get_base_query()
        esQuery = esQuery.filter('term', route=route)
        esQuery = esQuery.filter('range', date={
            "gte": start_date,
            "lte": end_date, "format": "yyyy-MM-dd"})
        esQuery = esQuery.filter('term', periodId=int(period))
        if day_type:
            esQuery = esQuery.filter('terms', dayType=day_type)

        aggs0 = A('terms', field='section', size=200)
        aggs0.metric('n_obs', 'sum', field='nObs')
        aggs0.metric('distance', 'sum', field='totalDistance')
        aggs0.metric('time', 'sum', field='totalTime')
        aggs0.metric('speed', 'bucket_script', script='params.d / params.t',
                     buckets_path={'d': 'distance', 't': 'time'})
        esQuery.aggs.bucket('sections', aggs0)

        aux_data = {}
        for sec in esQuery.execute().aggregations.sections.buckets:
            key = sec.key
            aux_data[key] = 3.6 * sec.speed.value

        result = []
        for i in range(len(limits) - 1):
            sp = aux_data.get(i, -1)
            interval = 6
            for i, bound in enumerate([0, 15, 19, 21, 23, 30]):
                if sp < bound:
                    interval = i
                    break
            result.append(interval)

        return result


class ESShapeHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "shape"
        super(ESShapeHelper, self).__init__(index_name)

    def get_route_shape(self, route, start_date, end_date):

        es_query = self.get_base_query()
        es_query = es_query.filter('term', route=route)
        es_query = es_query.filter('range', startDate={
            "gte": start_date,
            "lte": end_date,
            "format": "yyyy-MM-dd"
        })

        r = es_query.execute()

        if r.hits.total != 0:
            raise Exception()

        es_query = self.get_base_query()
        es_query = es_query.filter('term', route=route)
        es_query = es_query.filter('range', startDate={"lte": start_date, "format": "yyyy-MM-dd"})
        es_query = es_query.sort('-startDate')

        r = es_query.execute()

        if r.hits.total == 0:
            raise Exception()

        return (r.hits[0].points)
