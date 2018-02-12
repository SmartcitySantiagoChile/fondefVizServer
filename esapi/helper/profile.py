# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from elasticsearch_dsl import Search, A, Q
from elasticsearch_dsl.query import Match

from localinfo.models import Operator

from esapi.helper.basehelper import ElasticSearchHelper

from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryRouteParameterDoesNotExist


class ESProfileHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "profiles"
        super(ESProfileHelper, self).__init__(index_name)

    def get_base_params(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """

        es_time_period_query = self.get_unique_list_query("timePeriodInStartTime", size=50)
        es_day_type_query = self.get_unique_list_query("dayType", size=10)
        es_day_query = self.get_histogram_query("expeditionStartTime", interval="day", format="yyy-MM-dd")

        result = {
            'periods': es_time_period_query,
            'dayTypes': es_day_type_query,
            'days': es_day_query
        }

        return result

    def ask_for_profile_by_stop(self, start_date, end_date, day_type, stop_code, period, half_hour):
        """ return iterator to process load profile by stop """
        es_query = self.get_base_query()

        if stop_code is not None:
            es_query = es_query.query(
                Q({'term': {"authStopCode.keyword": stop_code}}) | Q({'term': {"userStopCode.keyword": stop_code}}) | Q(
                    {'term': {"userStopName.keyword": stop_code}}))
        else:
            raise ESQueryStopParameterDoesNotExist()

        if start_date is None or end_date is None:
            raise ESQueryDateRangeParametersDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStopTime=period)
        if half_hour:
            es_query = es_query.filter('terms', halfHour=half_hour)

        es_query = es_query.filter("range", expeditionStartTime={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        es_query = es_query.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'expeditionDayId',
                                    'userStopName', 'expandedAlighting', 'expandedBoarding', 'fulfillment',
                                    'stopDistanceFromPathStart', 'expeditionStartTime',
                                    'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                    'dayType', 'timePeriodInStopTime', 'loadProfile', 'busStation'])

        return es_query

    def ask_for_stop(self, term):
        """ ask to elasticsearch for a match values """

        es_auth_stop_query = Search().query(Match(authStopCode={"query": term, "analyzer": "standard"}))
        es_auth_stop_query = self.get_unique_list_query("authStopCode.keyword", size=15000, query=es_auth_stop_query)

        es_user_stop_query = Search().query(Match(userStopCode={"query": term, "analyzer": "standard"}))
        es_user_stop_query = self.get_unique_list_query("userStopCode.keyword", size=15000, query=es_user_stop_query)

        es_user_stop_name_query = Search().query(Match(userStopName={"query": term, "operator": "and"}))
        es_user_stop_name_query = self.get_unique_list_query("userStopName.keyword", size=15000,
                                                             query=es_user_stop_name_query)

        searches = {
            "1": es_auth_stop_query,
            "2": es_user_stop_query,
            "3": es_user_stop_name_query
        }
        result = self.make_multisearch_query_for_aggs(searches)

        return result

    def ask_for_available_days(self):
        searches = {
            "days": self.get_histogram_query("expeditionStartTime", interval="day", format="yyy-MM-dd")
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result

    def ask_for_available_routes(self):
        es_query = self.get_base_query()
        es_query = es_query[:0]
        es_query = es_query.source([])

        aggs = A('terms', field="route", size=5000)
        es_query.aggs.bucket('route', aggs)
        es_query.aggs['route']. \
            metric('additionalInfo', 'top_hits', size=1, _source=['operator', 'userRoute'])

        operator_list = [{"id": op[0], "text": op[1]} for op in Operator.objects.values_list('esId', 'name')]

        result = defaultdict(lambda: defaultdict(list))
        for hit in es_query.execute().aggregations.route.buckets:
            data = hit.to_dict()
            auth_route = data['key']
            operator_id = data['additionalInfo']['hits']['hits'][0]['_source']['operator']
            user_route = data['additionalInfo']['hits']['hits'][0]['_source']['userRoute']

            result[operator_id][user_route].append(auth_route)

        return result, operator_list

    def ask_for_profile_by_expedition(self, start_date, end_date, day_type, route, period, half_hour):

        es_query = self.get_base_query()

        """
        if expeditionId:
            esQuery = esQuery.filter('terms', expeditionDayId=expeditionId)
        if licensePlate:
            es_query = es_query.filter('terms', licensePlate=licensePlate)
        """

        if route:
            es_query = es_query.filter('term', route=route)
        else:
            raise ESQueryRouteParameterDoesNotExist()

        if day_type:
            es_query = es_query.filter('terms', dayType=day_type)
        if period:
            es_query = es_query.filter('terms', timePeriodInStartTime=period)
        if half_hour:
            half_hour = map(lambda x: int(x), half_hour)
            es_query = es_query.filter('terms', halfHourInStartTime=half_hour)

        if not start_date or not end_date:
            raise ESQueryDateRangeParametersDoesNotExist()

        es_query = es_query.filter("range", expeditionStartTime={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        es_query = es_query.source(['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'loadProfile',
                                    'expeditionDayId', 'userStopName', 'expandedAlighting', 'expandedBoarding',
                                    'expeditionStopOrder', 'stopDistanceFromPathStart', 'expeditionStartTime',
                                    'expeditionEndTime', 'authStopCode', 'userStopCode', 'timePeriodInStartTime',
                                    'dayType', 'timePeriodInStopTime', 'fulfillment', "busStation"])

        return es_query
