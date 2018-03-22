# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.downloader.datadownloader import DataDownloader, README_FILE_NAME
from rqworkers.dataDownloader.downloader.shape import ShapeFile
from rqworkers.dataDownloader.downloader.stop import StopFile

from esapi.helper.profile import ESProfileHelper

import os


class ProfileDataByExpedition(DataDownloader):
    """ Class that represents a profile downloader. """

    def __init__(self, es_client, es_query):
        DataDownloader.__init__(self, es_client, es_query, ESProfileHelper().get_index_name())
        self.column_dict = [
            {'es_name': 'operator', 'csv_name': 'Operador'},
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'userRoute', 'csv_name': 'Servicio_usuario'},
            {'es_name': 'licensePlate', 'csv_name': 'Patente'},
            {'es_name': 'authStopCode', 'csv_name': 'Código_parada_transantiago'},
            {'es_name': 'userStopCode', 'csv_name': 'Código_parada_usuario'},
            {'es_name': 'userStopName', 'csv_name': 'Nombre_parada'},
            {'es_name': 'expeditionStartTime', 'csv_name': 'Hora_inicio_expedición'},
            {'es_name': 'expeditionEndTime', 'csv_name': 'Hora_fin_expedición'},
            {'es_name': 'fulfillment', 'csv_name': 'Cumplimiento'},
            {'es_name': 'expeditionStopOrder', 'csv_name': 'Secuencia_parada'},
            {'es_name': 'expeditionDayId', 'csv_name': 'Identificador_expedición_día'},
            {'es_name': 'stopDistanceFromPathStart', 'csv_name': 'Distancia_parada_desde_inicio_ruta'},
            {'es_name': 'expandedBoarding', 'csv_name': 'Subidas_expandidas'},
            {'es_name': 'expandedAlighting', 'csv_name': 'Bajadas_expandidas'},
            {'es_name': 'loadProfile', 'csv_name': 'Perfil_carga_al_llegar'},
            {'es_name': 'busCapacity', 'csv_name': 'Capacidad_bus'},
            {'es_name': 'expeditionStopTime', 'csv_name': 'Hora_en_parada'},
            {'es_name': 'timePeriodInStartTime', 'csv_name': 'Periodo_transantiago_inicio_expedicion'},
            {'es_name': 'timePeriodInStopTime', 'csv_name': 'Periodo_transantiago_parada_expedición'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_dia'},
            {'es_name': 'busStation', 'csv_name': 'Zona_paga'},
            {'es_name': 'transactions', 'csv_name': 'Número_transacciones_en_parada'},
            {'es_name': 'halfHourInStartTime', 'csv_name': 'Media_hora_de_inicio_expedición'},
            {'es_name': 'halfHourInStopTime', 'csv_name': 'Media_hora_en_parada'},
        ]
        self.translator = self.create_translator()

    def get_data_file_name(self):
        return 'Perfil.csv'

    def add_additional_files(self, zip_file_obj):
        # save shape file in zipfile
        def get_route():
            for query_filter in self.es_query['query']['bool']['filter']:
                if 'term' in query_filter and 'route' in query_filter['term']:
                    return query_filter

        route = get_route()
        shape_query = {'query': {'bool': {'filter': {'term': {'route': route}}}}}
        shape_downloader = ShapeFile(self.es_client, shape_query)
        shape_downloader.download(zip_file_obj)
        additional_file = '\t- {0}: Geometría del servicio\r\n'.format(shape_downloader.get_data_file_name())

        stop_query = {'query': {'bool': {'filter': {'term': {'authRouteCode': route}}}}}
        stop_downloader = StopFile(self.es_client, stop_query)
        stop_downloader.download(zip_file_obj)
        additional_file += '\t- {0}: Secuencia de parada\r\n'.format(stop_downloader.get_data_file_name())

        # create readme file
        file_name = 'profile.readme'
        file_path = os.path.join(os.path.dirname(__file__), '..', 'helpfiles', file_name)
        with open(file_path, 'r') as input_file:
            content = input_file.read()
            filter_description = self.get_filter_criteria().encode('utf-8')
            content.replace('\n'.encode('utf-8'), '\r\n'.encode('utf-8'))
            content = content.replace('<put_filters_here>'.encode('utf-8'), filter_description)
            additional_files = '<put_additional_files_here>'.encode('utf-8')
            content = content.replace(additional_files, additional_file.encode('utf-8'))

        zip_file_obj.writestr(README_FILE_NAME, content)

    def row_parser(self, row):

        formatted_row = []
        for column_name in self.get_fields():
            value = row[column_name]
            try:
                if column_name == 'dayType':
                    value = self.day_type_dict[value]
                elif column_name == 'operator':
                    value = self.operator_dict[value]
                elif column_name in ['timePeriodInStartTime', 'timePeriodInStopTime']:
                    value = self.timeperiod_dict[value]
                elif column_name in ['halfHourInStartTime', 'halfHourInStopTime']:
                    value = self.halfhour_dict[value]
            except KeyError:
                value = ""

            if isinstance(value, (int, float)):
                value = str(value)
            elif value is None:
                value = ""

            formatted_row.append(value)

        return formatted_row


class ProfileDataByStop(ProfileDataByExpedition):

    def __init__(self, es_query, index_name):
        ProfileDataByExpedition.__init__(self, es_query, index_name)

    def add_additional_files(self, zip_file_obj):
        pass
