from django.conf import settings

from elasticsearch_dsl import Search, A, MultiSearch


class ElasticSearchHelper(object):
    """ helper to ask elasticsearch """

    def __init__(self, index_name):

        if index_name is None:
            raise ValueError("Index name can't be none")

        self.index_name = index_name
        self.client = settings.ES_CLIENT

    def get_base_query(self):
        """ get query object with index and client assigned  """
        return Search(using=self.client, index=self.index_name)

    def make_multisearch_query_for_aggs(self, es_query_dict):
        """ make multisearch request to es with aggregation """
        multiSearch = MultiSearch(using=self.client, index=self.index_name)

        keys = []
        for key, esQuery in es_query_dict.iteritems():
            multiSearch = multiSearch.add(esQuery)
            keys.append(key)
        
        # to see the query generated
        #print multiSearch.to_dict()
        responses = multiSearch.execute()

        result = {}
        for index, response in enumerate(responses):
            resultList = []
            for tag in response.aggregations.unique.buckets:
                if tag.doc_count == 0:
                    continue

                if "key_as_string" in tag:
                    resultList.append(tag.key_as_string)
                else:
                    resultList.append(tag.key)
            resultList.sort()

            result[keys[index]] = resultList

        return result

    def get_histogram_query(self, field, interval, format):
        """ create agregation query of histogram """

        query = Search()
        query = query[:0]
        query.aggs.bucket("unique", "date_histogram",
                          field=field,
                          interval=interval,
                          format=format)
        return query

    def get_unique_list_query(self, field, size=0, query=None):
        """ create query to get unique list of values from field """

        if query is None:
            query = Search()

        query = query[:0]
        aggs = A('terms', field=field, size=size)
        query.aggs.bucket('unique', aggs)

        return query
