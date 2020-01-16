from django.conf import settings

from elasticsearch_dsl import Search, A, MultiSearch
from elasticsearch.exceptions import ConnectionTimeout


class ElasticSearchHelper(object):
    """ helper to ask elasticsearch """

    def __init__(self, index_name, file_extensions):

        if index_name is None or index_name == '':
            raise ValueError("Index name can't be none")

        self._index_name = index_name
        self._file_extensions = file_extensions
        self.client = settings.ES_CLIENT

    @property
    def index_name(self):
        return self._index_name

    @property
    def file_extensions(self):
        """
        file extension that can manipulate this helper
        :return: list of file extensions
        """
        return self._file_extensions

    def get_base_query(self):
        """ get query object with index and client assigned  """
        return Search(using=self.client, index=self.index_name)

    def get_attr_list(self, es_query_result, aggs_name, sort=True):
        """
        Extract key from aggregation query
        :param es_query_result: Search object
        :param aggs_name: aggregation name present in @es_query_result
        :param sort: if return sorted values, default: True
        :return: list of values
        """
        result_list = []
        for tag in es_query_result.aggregations[aggs_name].buckets:
            if tag.doc_count == 0:
                continue

            if "key_as_string" in tag:
                result_list.append(tag.key_as_string)
            else:
                result_list.append(tag.key)

        if sort:
            result_list.sort()

        return result_list

    def make_multisearch_query_for_aggs(self, *args, **kwargs):
        """
        Make multisearch request to es with aggregation
        :param args: list of queries
        :return: list of result for each query
        """
        multi_search = MultiSearch(using=self.client, index=self.index_name)

        for es_query in args:
            multi_search = multi_search.add(es_query)

        result = multi_search.execute()
        flat = kwargs.get('flat', False)
        if len(result) == 1 and flat:
            return result[0]

        return result

    def get_histogram_query(self, field, interval, date_format, time_zone=None, es_query=None):
        """ create aggregation query of histogram """

        kwargs = {}
        if time_zone is not None:
            kwargs['time_zone'] = time_zone

        if es_query is None:
            es_query = self.get_base_query()[:0]

        es_query.aggs.bucket("unique", "date_histogram",
                             field=field,
                             interval=interval,
                             format=date_format, **kwargs)
        return es_query

    def get_unique_list_query(self, field, size=0, query=None):
        """ create query to get unique list of values from field """

        if query is None:
            query = self.get_base_query()

        query = query[:0]
        aggs = A('terms', field=field, size=size)
        query.aggs.bucket('unique', aggs)

        return query

    def _get_available_days(self, field, valid_operator_list=None, time_zone=None):

        es_query = None
        if valid_operator_list:
            es_query = self.get_base_query()[:0]
            es_query = es_query.filter('terms', operator=valid_operator_list)

        es_query = self.get_histogram_query(field, interval="day", date_format="yyy-MM-dd", es_query=es_query,
                                            time_zone=time_zone)

        result = self.get_attr_list(self.make_multisearch_query_for_aggs(es_query, flat=True), 'unique')

        return result

    def get_data_by_file(self, file_filter=None):
        """
        return query with files and doc number associated to them
        :param file_filter: list of path. I.e. ['2017-01-01.extension', ...]
        :return: Search object
        """

        es_query = self.get_base_query()[:0]
        if file_filter is not None:
            es_query = es_query.filter('terms', path=file_filter)
        aggs = A('terms', field="path", size=5000)
        es_query.aggs.bucket('files', aggs)

        return es_query

    def delete_data_by_file(self, file_name):

        es_query = self.get_base_query()
        es_query = es_query.filter('term', path=file_name)

        try:
            # if query select a lot of files this call will fail with timeout
            return es_query.delete()
        except ConnectionTimeout:
            return None
