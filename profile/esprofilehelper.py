from bowerapp.eshelper.eshelper import ElasticSearchHelper

from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Match


class ESProfileHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "profiles"
        super(ESProfileHelper, self).__init__(index_name)

    def get_base_params(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """

        esTimePeriodQuery = self.get_unique_list_query("timePeriodInStartTime", size=50)
        esDayTypeQuery = self.get_unique_list_query("dayType", size=10)
        esDayQuery = self.get_histogram_query("expeditionStartTime", interval="day", format="yyy-MM-dd")
        esAuthRouteQuery = self.get_unique_list_query("route", size=10000)
        esUserRouteQuery = self.get_unique_list_query("userRoute", size=10000)

        result = {}
        result['periods'] = esTimePeriodQuery
        result['dayTypes'] = esDayTypeQuery
        result['days'] = esDayQuery
        result["auth_routes"] = esAuthRouteQuery
        result["user_routes"] = esUserRouteQuery

        return result

    def ask_for_stop(self, term):
        """ ask to elasticsearch for a match values """

        esAuthStopQuery = Search().query(Match(authStopCode={"query": term, "analyzer": "standard"}))
        esAuthStopQuery = self.get_unique_list_query("authStopCode.keyword", size=15000, query=esAuthStopQuery)

        esUserStopQuery = Search().query(Match(userStopCode={"query": term, "analyzer": "standard"}))
        esUserStopQuery = self.get_unique_list_query("userStopCode.keyword", size=15000, query=esUserStopQuery)

        esUserStopNameQuery = Search().query(Match(userStopName={"query": term, "operator": "and"}))
        esUserStopNameQuery = self.get_unique_list_query("userStopName.keyword", size=15000, query=esUserStopNameQuery)

        searches = {
            "1": esAuthStopQuery,
            "2": esUserStopQuery,
            "3": esUserStopNameQuery
        }
        result = self.make_multisearch_query_for_aggs(searches)

        return result

    def ask_for_available_days(self):
        searches = {
            "days": self.get_histogram_query("expeditionStartTime", interval="day", format="yyy-MM-dd")
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result

class ESODByRouteHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "odbyroute"
        super(ESODByRouteHelper, self).__init__(index_name)

    def get_base_params(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """

        esTimePeriodQuery = self.get_unique_list_query("timePeriodInStopTime", size=50)
        esDateQuery = self.get_histogram_query("date", interval="day", format="yyy-MM-dd")
        esRouteQuery = self.get_unique_list_query("authRouteCode", size=10000)

        result = {}
        result['periods'] = esTimePeriodQuery
        result['days'] = esDateQuery
        result['routes'] = esRouteQuery

        return result

    def ask_for_od(self, auth_route_code, time_periods, day_type, days):
        """ ask to elasticsearch for a match values """

        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        if time_periods:
            es_query = es_query.filter('terms', timePeriodInStopTime=time_periods)
        if day_type:
            es_query = es_query.filter('term', dayType=day_type)
        if days:
            es_query = es_query.filter('range', date={'gte': days})

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
        matrix.sort(key=lambda e: e['origin']['order'])

        return matrix, max_value


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        super(ESStopHelper, self).__init__(index_name)

    def get_stop_list(self, auth_route_code, day, flat=False,
                      fields=('userStopCode', 'authStopCode', 'stopName', 'latitude', 'longitude', 'order')):
        """ ask to elasticsearch for a match values """

        es_query = self.get_base_query().filter('term', authRouteCode=auth_route_code)
        if day:
            es_query = es_query.filter('range', date={'gte': day, 'lte': day, 'format': 'yyyy-MM-dd'})

        # there is not route with more than 500 stops
        es_query = es_query[:500]
        es_query = es_query.sort('order')
        es_query = es_query.source(fields)

        stop_list = [stop.to_dict() for stop in es_query.execute()]

        if flat:
            # assume that dict has just one attribute
            key = stop_list[0].keys()[0]
            stop_list = [dict_obj[key] for dict_obj in stop_list]

        return stop_list
