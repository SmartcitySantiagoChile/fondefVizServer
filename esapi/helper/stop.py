# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search, A, Q
from elasticsearch_dsl.query import Match

from esapi.helper.basehelper import ElasticSearchHelper
from esapi.errors import ESQueryStopParameterDoesNotExist, ESQueryDateParametersDoesNotExist, \
    ESQueryStopInfoDoesNotExist


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

    def get_stop_info(self, dates, auth_stop_code):
        """ ask to elasticsearch for a match values """
        es_query = self.get_base_query()
        es_query = es_query.filter('term', **{'authCode.raw': auth_stop_code})

        if not auth_stop_code:
            raise ESQueryStopParameterDoesNotExist()

        start_date = dates[0][0]
        if not start_date:
            raise ESQueryDateParametersDoesNotExist()

        es_query = self.get_base_query().filter('term', **{'authCode.raw': auth_stop_code})
        es_query = es_query.filter('range', startDate={
            'lte': start_date,
            'format': 'yyyy-MM-dd'
        }).sort('-startDate')[:1]

        try:
            stop_info = es_query.execute().hits.hits[0]['_source']
            del stop_info['path']
            del stop_info['timestamp']
        except IndexError:
            raise ESQueryStopInfoDoesNotExist()

        return stop_info
