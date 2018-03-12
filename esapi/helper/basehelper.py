from django.conf import settings

from elasticsearch_dsl import Search, A, MultiSearch


class ElasticSearchHelper(object):
    """ helper to ask elasticsearch """

    def __init__(self, index_name):

        if index_name is None or index_name == '':
            raise ValueError("Index name can't be none")

        self.index_name = index_name
        self.client = settings.ES_CLIENT

    def get_index_name(self):
        return self.index_name

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
        # print multiSearch.to_dict()
        responses = multi_search.execute()

        result = {}
        for index, response in enumerate(responses):
            result_list = []
            aggregation_properties = dir(response.aggregations)
            if len(aggregation_properties) == 1 and aggregation_properties[0] == 'unique':
                for tag in response.aggregations.unique.buckets:
                    if tag.doc_count == 0:
                        continue

                    if "key_as_string" in tag:
                        result_list.append(tag.key_as_string)
                    else:
                        result_list.append(tag.key)
                result_list.sort()

                result[keys[index]] = result_list
            else:
                result[keys[index]] = response.to_dict()

        return result

    def get_histogram_query(self, field, interval, date_format, time_zone=None, es_query=None):
        """ create aggregation query of histogram """

        kwargs = {}
        if time_zone is not None:
            kwargs['time_zone'] = time_zone

        if es_query is None:
            es_query = Search()[:0]

        es_query.aggs.bucket("unique", "date_histogram",
                             field=field,
                             interval=interval,
                             format=date_format, **kwargs)
        return es_query

    def get_unique_list_query(self, field, size=0, query=None):
        """ create query to get unique list of values from field """

        if query is None:
            query = Search()

        query = query[:0]
        aggs = A('terms', field=field, size=size)
        query.aggs.bucket('unique', aggs)

        return query

    def get_available_days(self, field, valid_operator_list=None, time_zone=None):

        es_query = None
        if valid_operator_list:
            es_query = self.get_base_query()[:0]
            es_query = es_query.filter('terms', operator=valid_operator_list)

        searches = {
            "days": self.get_histogram_query(field, interval="day", date_format="yyy-MM-dd", es_query=es_query,
                                             time_zone=time_zone)
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result

    def get_data_by_file(self):
        """ return query with files and doc number associated to them """

        es_query = self.get_base_query()[:0]
        aggs = A('terms', field="path", size=5000)
        es_query.aggs.bucket('files', aggs)

        return es_query

    def delete_data_by_file(self, file_name):

        es_query = self.get_base_query()
        es_query = es_query.filter('term', path=file_name)

        return es_query.delete()
