# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import A

from localinfo.helper import get_operator_list_for_select_input

from esapi.errors import ESQueryResultEmpty, ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESODByRouteHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "odbyroute"
        super(ESODByRouteHelper, self).__init__(index_name)

    def get_base_params(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """

        es_time_period_query = self.get_unique_list_query("timePeriodInStopTime", size=50)
        es_date_query = self.get_histogram_query("date", interval="day", date_format="yyy-MM-dd")
        es_route_query = self.get_unique_list_query("authRouteCode", size=10000)

        result = {
            'periods': es_time_period_query,
            'days': es_date_query,
            'routes': es_route_query
        }

        return result

    def ask_for_available_days(self, valid_operator_list):
        return self.get_available_days('date', valid_operator_list)

    def ask_for_available_routes(self, valid_operator_list):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist

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

    def ask_for_od(self, auth_route_code, time_periods, day_type, start_date, end_date, valid_operator_list):
        """ ask to elasticsearch for a match values """

        es_query = self.get_base_query()

        if valid_operator_list:
            es_query = es_query.filter('terms', operator=valid_operator_list)
        else:
            raise ESQueryOperatorParameterDoesNotExist()

        if auth_route_code:
            es_query = es_query.filter('term', authRouteCode=auth_route_code)
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if time_periods:
            es_query = es_query.filter('terms', timePeriodInStopTime=time_periods)
        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if start_date and end_date:
            es_query = es_query.filter("range", date={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })

        es_query = es_query[:0]
        es_query = es_query.source([])

        aggs = A('terms', field="authStartStopCode", size=500)
        es_query.aggs.bucket('start', aggs).bucket('end', 'terms', field="authEndStopCode")
        # add metrics to start bucket
        es_query.aggs['start']. \
            metric('additionalInfo', 'top_hits', size=1,
                   _source=['startStopOrder', 'userStartStopCode', 'startStopName'])
        # add metrics to end bucket
        es_query.aggs['start']['end']. \
            metric('expandedTripNumber', 'sum', field='expandedTripNumber'). \
            metric('additionalInfo', 'top_hits', size=1, _source=['endStopOrder', 'userEndStopCode', 'endStopName'])

        matrix = []
        max_value = 0
        for hit in es_query.execute().aggregations.start.buckets:
            data = hit.to_dict()
            start = {
                'authStopCode': data['key'],
                'userStopCode': data['additionalInfo']['hits']['hits'][0]["_source"]["userStartStopCode"],
                'userStopName': data['additionalInfo']['hits']['hits'][0]["_source"]["startStopName"],
                'order': data['additionalInfo']['hits']['hits'][0]["_source"]["startStopOrder"]
            }
            destination = []
            for end_data in data['end']['buckets']:
                end = end_data['key']
                value = end_data['expandedTripNumber']['value']
                max_value = max(max_value, value)
                destination.append({
                    'authStopCode': end,
                    'userStopCode': end_data['additionalInfo']['hits']['hits'][0]["_source"]["userEndStopCode"],
                    'userStopName': end_data['additionalInfo']['hits']['hits'][0]["_source"]["endStopName"],
                    'order': end_data['additionalInfo']['hits']['hits'][0]["_source"]["endStopOrder"],
                    'value': value
                })
            destination.sort(key=lambda e: e['order'])
            matrix.append({
                'origin': start,
                'destination': destination
            })

        if len(matrix) == 0:
            raise ESQueryResultEmpty()

        matrix.sort(key=lambda e: e['origin']['order'])

        return matrix, max_value
