# -*- coding: utf-8 -*-


from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, ProfileCSVHelper, ShapeCSVHelper, StopByRouteCSVHelper


class ProfileByExpeditionData(object):
    """ class that build profile csv """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.profile_file = ProfileCSVHelper(self.es_client, self.es_query)

    def get_routes(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'term' in query_filter and 'route' in query_filter['term']:
                return [query_filter['term']['route']]
            if 'terms' in query_filter and 'route' in query_filter['terms']:
                return query_filter['terms']['route']

    def get_date_range(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'bool' in query_filter:
                should = query_filter['bool']['should']
                field_a = list(should[0]['range'].keys())[0]
                field_b = list(should[-1]['range'].keys())[0]

                gte = should[0]['range'][field_a]["gte"].replace("||/d", "")
                lte = should[-1]['range'][field_b]["lte"].replace("||/d", "")
                return gte, lte
            elif 'range' in query_filter:
                field = list(query_filter['range'].keys())[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")
                return gte, lte

    def get_filters(self):
        return self.profile_file.get_filter_criteria(ProfileCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.profile_file.download(zip_manager)

        routes = self.get_routes()

        start_date, end_date = self.get_date_range()

        shape_file = ShapeCSVHelper(self.es_client)
        shape_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        stop_file = StopByRouteCSVHelper(self.es_client)
        stop_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        help_file_title = 'ARCHIVO DE PERFILES'
        files_description = [self.profile_file.get_file_description(), shape_file.get_file_description(),
                             stop_file.get_file_description()]
        data_filter = self.profile_file.get_filter_criteria(ProfileCSVHelper.FORMATTER_FOR_FILE)
        explanation = self.profile_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "".join(files_description), data_filter, explanation)


class ProfileDataByStop(object):

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.profile_file = ProfileCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.profile_file.get_filter_criteria(ProfileCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.profile_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE PERFILES'
        files_description = [self.profile_file.get_file_description()]
        data_filter = self.profile_file.get_filter_criteria(ProfileCSVHelper.FORMATTER_FOR_FILE)
        explanation = self.profile_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "".join(files_description), data_filter, explanation)
