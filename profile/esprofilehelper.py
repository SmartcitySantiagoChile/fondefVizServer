from bowerapp.eshelper.eshelper import ElasticSearchHelper

from elasticsearch_dsl import Search
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

        result = {}
        result['periods'] = esTimePeriodQuery
        result['dayTypes'] = esDayTypeQuery
        result['days'] = esDayQuery

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

