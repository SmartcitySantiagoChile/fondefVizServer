# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import Search, A

from bowerapp.eshelper.eshelper import ElasticSearchHelper

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

        return d_data


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
