# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Match

from esapi.helper.basehelper import ElasticSearchHelper


class ESStopHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stop"
        file_extensions = ['stop']
        super(ESStopHelper, self).__init__(index_name, file_extensions)

    def get_matched_stop_list(self, term):
        """ ask to elasticsearch for a match values """

        es_auth_stop_query = Search().query(Match(authCode={"query": term, "analyzer": "standard"}))[:0]
        aggs = A('terms', field='authCode.raw', size=100)
        es_auth_stop_query.aggs.bucket('unique', aggs)
        es_auth_stop_query.aggs['unique'].metric('additional_info', 'top_hits', size=1, _source=['authCode'])

        es_user_stop_query = Search().query(Match(userCode={"query": term, "analyzer": "standard"}))[:0]
        aggs = A('terms', field='userCode.raw', size=100)
        es_user_stop_query.aggs.bucket('unique', aggs)
        es_user_stop_query.aggs['unique'].metric('additional_info', 'top_hits', size=1, _source=['authCode'])

        es_user_stop_name_query = Search().query(
            Match(name={"query": term, "operator": "and", "analyzer": "autocomplete_analyzer"}))[:0]
        aggs = A('terms', field='name.raw', size=100, order={"max_score": "desc"})
        es_user_stop_name_query.aggs.bucket('unique', aggs)
        es_user_stop_name_query.aggs['unique'].metric('max_score', 'max', script={'source': '_score'})
        es_user_stop_name_query.aggs['unique'].metric('additional_info', 'top_hits', _source=['authCode'])

        results = self.make_multisearch_query_for_aggs(es_auth_stop_query, es_user_stop_query, es_user_stop_name_query)

        answer = []
        for result in results:
            answer += [(ans.key, ans.additional_info.hits[0].authCode) for ans in result.aggregations.unique.buckets]

        return answer
