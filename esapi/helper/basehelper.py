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
        multi_search = MultiSearch(using=self.client, index=self.index_name)

        keys = []
        for key, es_query in es_query_dict.iteritems():
            multi_search = multi_search.add(es_query)
            keys.append(key)

        # to see the query generated
        #print multiSearch.to_dict()
        responses = multi_search.execute()

        result = {}
        for index, response in enumerate(responses):
            result_list = []
            print(response)
            print(response.agregations)
            print(response.agregations.unique)
            print(type(response.agregations.unique.buckets))
            print(type(response.buckets))
            print(list(response.buckets))
            print(response.agregations.unique.buckets)
            print(response.buckets)
            for tag in response.aggregations.unique.buckets:
                if tag.doc_count == 0:
                    continue

                if "key_as_string" in tag:
                    result_list.append(tag.key_as_string)
                else:
                    result_list.append(tag.key)
            result_list.sort()

            result[keys[index]] = result_list

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
