# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.downloader.datadownloader import DataDownloader

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_operator_list_for_select_input, get_halfhour_list_for_select_input


class ProfileData(DataDownloader):
    """ Class that represents a profile downloader. """

    def __init__(self):
        DataDownloader.__init__(self)
        self.operator_dict = get_operator_list_for_select_input(to_dict=True)
        self.day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        self.get_timeperiod_dict = get_timeperiod_list_for_select_input(to_dict=True)
        self.get_halfhour_dict = get_halfhour_list_for_select_input(to_dict=True, format='name')

    def get_data_file_name(self):
        return 'Perfil.csv'

    def get_header(self):
        return ['Operador', 'Servicio_transantiago', 'Servicio_usuario', 'Patente', 'Código_parada_transantiago',
                'Código_parada_usuario', 'Nombre_parada', 'Hora_inicio_expedición', 'Hora_fin_expedición',
                'Cumplimiento', 'Secuencia_parada', 'Identificador_expedición_día',
                'Distancia_parada_desde_inicio_ruta', 'Subidas_expandidas', 'Bajadas_expandidas',
                'Perfil_carga_al_llegar', 'Capacidad_bus', 'Hora_detención_en_parada',
                'Periodo_transantiago_inicio_expedicion', 'Periodo_transantiago_parada_expedición', 'Tipo_dia',
                'Zona_paga', 'Número_transacciones_en_parada', 'Media_hora_de_inicio_expedición',
                'Media_hora_en_parada']

    def get_fields(self):
        return ['operator', 'route', 'userRoute', 'licensePlate', 'authStopCode', 'userStopCode',
                'userStopName', 'expeditionStartTime', 'expeditionEndTime', 'fulfillment',
                'expeditionStopOrder', 'expeditionDayId', 'stopDistanceFromPathStart', 'expandedBoarding',
                'expandedAlighting', 'loadProfile', 'busCapacity', 'expeditionStopTime',
                'timePeriodInStartTime', 'timePeriodInStopTime', 'dayType', 'busStation', 'transactions',
                'halfHourInStartTime', 'halfHourInStopTime']

    def add_additional_files(self, zip_file_obj):
        # copy readme file
        with zip_file_obj.write("Léeme.txt", 'w') as output_file:
            with open('profile.readme', 'rb') as input_file:
                content = input_file.read()
                # incluir filtros y archivos adicionales
                output_file.write(content)

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
                    value = self.get_timeperiod_dict[value]
                elif column_name in ['halfHourInStartTime', 'halfHourInStopTime']:
                    value = self.get_halfhour_dict[column_name]
            except KeyError:
                value = None

            formatted_row.append(value)

        return formatted_row
