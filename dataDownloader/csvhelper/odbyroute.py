# -*- coding: utf-8 -*-


from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, ODByRouteCSVHelper, ShapeCSVHelper, StopByRouteCSVHelper


class OdByRouteData(object):
    """ Class that represents an odbyroute file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.od_by_route_file = ODByRouteCSVHelper(self.es_client, self.es_query)

    def get_routes(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'term' in query_filter and 'authRouteCode' in query_filter['term']:
                return [query_filter['term']['authRouteCode']]
            if 'terms' in query_filter and 'authRouteCode' in query_filter['terms']:
                return query_filter['terms']['authRouteCode']

    def get_date_range(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'range' in query_filter:
                field = list(query_filter['range'].keys())[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")
                return gte, lte

    def get_filters(self):
        return self.od_by_route_file.get_filter_criteria(ODByRouteCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.od_by_route_file.download(zip_manager)

        routes = self.get_routes()
        start_date, end_date = self.get_date_range()

        shape_file = ShapeCSVHelper(self.es_client)
        shape_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        stop_file = StopByRouteCSVHelper(self.es_client)
        stop_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        help_file_title = 'ARCHIVO DE MATRIZ DE ETAPA POR SERVICIO'
        files_description = [self.od_by_route_file.get_file_description(), shape_file.get_file_description(),
                             stop_file.get_file_description()]
        data_filter = self.od_by_route_file.get_filter_criteria(ODByRouteCSVHelper.FORMATTER_FOR_FILE)
        explanation = self.od_by_route_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "".join(files_description), data_filter, explanation)
