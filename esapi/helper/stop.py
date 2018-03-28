# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Match

from esapi.helper.basehelper import ElasticSearchHelper


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        super(ESStopHelper, self).__init__(index_name)

    def get_matched_stop_list(self, term):
        """ ask to elasticsearch for a match values """

        es_auth_stop_query = Search().query(Match(authCode={"query": term, "analyzer": "standard"}))[:0]
        aggs = A('terms', field='authCode.raw', size=100)
        es_auth_stop_query.aggs.bucket('unique', aggs)
        es_auth_stop_query.aggs['unique'].metric('additional_info', 'top_hits', size=1, _source=['userCode'])

        es_user_stop_query = Search().query(Match(userCode={"query": term, "analyzer": "standard"}))
        aggs = A('terms', field='userCode.raw', size=100)
        es_auth_stop_query.aggs.bucket('unique', aggs)
        es_auth_stop_query.aggs['unique'].metric('additional_info', 'top_hits', size=1, _source=['userCode'])

        es_user_stop_name_query = Search().query(
            Match(userName={"query": term, "operator": "and", "analyzer": "autocomplete_analyzer"}))[:0]
        aggs = A('terms', field='userName.raw', size=100, order={"max_score": "desc"})
        es_user_stop_name_query.aggs.bucket('results', aggs)
        es_user_stop_name_query.aggs['results'].metric('max_score', 'max', script={'source': '_score'})
        es_user_stop_name_query.aggs['results'].metric('additional_info', 'top_hits', _source=['userCode'])

        searches = {
            "1": es_auth_stop_query,
            "2": es_user_stop_query,
            "3": es_user_stop_name_query
        }
        result = self.make_multisearch_query_for_aggs(searches)

        result["3"] = [x["key"] for x in result["3"]["aggregations"]["results"]["buckets"]]

        return result
