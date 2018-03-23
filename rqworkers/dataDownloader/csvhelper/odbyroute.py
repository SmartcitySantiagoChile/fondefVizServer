# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.csvhelper.helper import ZipManager, ODByRouteCSVHelper, ShapeCSVHelper, StopCSVHelper


class OdByRouteData(object):
    """ Class that represents an odbyroute file. """

    def __init__(self, es_client, es_query):
        self.es_query = es_query
        self.es_client = es_client

    def get_routes(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'term' in query_filter and 'authRouteCode' in query_filter['term']:
                return [query_filter['term']['authRouteCode']]
            if 'terms' in query_filter and 'authRouteCode' in query_filter['terms']:
                return query_filter['terms']['authRouteCode']

    def get_date_range(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'range' in query_filter:
                field = query_filter['range'].keys()[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")
                return gte, lte

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        od_by_route_file = ODByRouteCSVHelper(self.es_client, self.es_query)
        od_by_route_file.download(zip_manager)

        routes = self.get_routes()
        start_date, end_date = self.get_date_range()

        shape_file = ShapeCSVHelper(self.es_client)
        shape_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        stop_file = StopCSVHelper(self.es_client)
        stop_file.download(zip_manager, routes=routes, start_date=start_date, end_date=end_date)

        template = 'odbyroute.readme'
        files_description = [od_by_route_file.get_file_description(), shape_file.get_file_description(),
                             stop_file.get_file_description()]
        data_filter = od_by_route_file.get_filter_criteria()
        zip_manager.build_readme(template, "\r\n".join(files_description), data_filter)
