# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.csvhelper.helper import ZipManager, SpeedCSVHelper, ShapeCSVHelper, StopCSVHelper


class SpeedDataWithShapeAndRoute(object):
    """ Class that build speed csv """

    def __init__(self, es_client, es_query):
        self.es_query = es_query
        self.es_client = es_client

    def get_route(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'term' in query_filter and 'authRouteCode' in query_filter['term']:
                return query_filter['term']['authRouteCode']

    def get_date_range(self):
        for query_filter in self.es_query['query']['bool']['filter']:
            if 'range' in query_filter:
                field = query_filter['range'].keys()[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")
                return gte, lte

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        speed_file = SpeedCSVHelper(self.es_client, self.es_query)
        speed_file.download(zip_manager)

        route = self.get_route()
        start_date, end_date = self.get_date_range()

        shape_file = ShapeCSVHelper(self.es_client)
        shape_file.download(zip_manager, route=route, start_date=start_date, end_date=end_date)

        stop_file = StopCSVHelper(self.es_client)
        stop_file.download(zip_manager, route=route, start_date=start_date, end_date=end_date)

        template = 'speed.readme'
        files_description = [speed_file.get_file_description(), shape_file.get_file_description(),
                             stop_file.get_file_description()]
        data_filter = speed_file.get_filter_criteria()
        zip_manager.build_readme(template, "\r\n".join(files_description), data_filter)


class SpeedData(object):
    """ Class that build speed csv """

    def __init__(self, es_client, es_query):
        self.es_query = es_query
        self.es_client = es_client

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        speed_file = SpeedCSVHelper(self.es_client, self.es_query)
        speed_file.download(zip_manager)

        template = 'speed.readme'
        files_description = [speed_file.get_file_description()]
        data_filter = speed_file.get_filter_criteria()
        zip_manager.build_readme(template, "\r\n".join(files_description), data_filter)
