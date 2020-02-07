# -*- coding: utf-8 -*-


from collections import defaultdict

from elasticsearch_dsl import A, Q

from esapi.errors import ESQueryResultEmpty, ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist, \
    ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper
from localinfo.helper import get_operator_list_for_select_input
from functools import reduce


class ESODByRouteHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "odbyroute"
        file_extensions = ['odbyroute']
        super(ESODByRouteHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('date', valid_operator_list)

    def get_available_routes(self, valid_operator_list):
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

    def get_base_query_for_od(self, auth_route_code, time_periods, day_type, dates, valid_operator_list):
        """ base query to get raw data """
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

        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[-1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q("range", date={
                "gte": start_date + "||/d",
                "lte": end_date + "||/d",
                "format": "yyyy-MM-dd",
                "time_zone": "+00:00"
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])

        return es_query

    def get_od_data(self, auth_route_code, time_periods, day_type, dates, valid_operator_list):
        """ ask to elasticsearch for a match values """

        es_query = self.get_base_query_for_od(auth_route_code, time_periods, day_type, dates,
                                              valid_operator_list)[:0]
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
