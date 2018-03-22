# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.downloader.datadownloader import DataDownloader

from esapi.helper.shape import ESShapeHelper


class ShapeFile(DataDownloader):
    """ Class that represents a shape file. """

    def __init__(self, es_client, es_query):
        DataDownloader.__init__(self, es_client, es_query, ESShapeHelper().get_index_name())

        self.column_dict = [
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación'},
            {'es_name': 'points', 'csv_name': 'Latitud,Longitud'}
        ]
        self.translator = self.create_translator()

    def get_data_file_name(self):
        return 'Geometría.csv'

    def add_additional_files(self, zip_file_obj):
        # nothing to do here
        pass

    def row_parser(self, row):
        rows = []

        route = row['route']
        start_date = row['startDate']
        points = row['stops']

        for point in points:
            shape_row = [
                route,
                start_date,
                str(point['latitude']),
                str(point['longitude']),
                str(point['segmentStart']),
            ]
            rows.append(shape_row)

        return rows
