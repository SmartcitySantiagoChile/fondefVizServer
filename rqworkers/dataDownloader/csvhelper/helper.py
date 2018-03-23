# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search

from rqworkers.dataDownloader.unicodecsv import UnicodeWriter
from rqworkers.dataDownloader.errors import FilterHasToBeListErrpr

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_operator_list_for_select_input, get_halfhour_list_for_select_input, get_commune_list_for_select_input

from esapi.helper.profile import ESProfileHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.odbyroute import ESODByRouteHelper

import os
import zipfile
import uuid

README_FILE_NAME = 'Léeme.txt'

PROFILE_BY_EXPEDITION_DATA = 'profile_by_expedition'
PROFILE_BY_STOP_DATA = 'profile_by_stop'
OD_BY_ROUTE_DATA = 'od_by_route_data'
SHAPE_DATA = 'shape_data'
STOP_DATA = 'stop_data'
SPEED_MATRIX_DATA = 'speed_matrix_data'
TRIP_DATA = 'trip_data'


class ZipManager:
    """ to manage zip file """

    def __init__(self, file_path):
        self.file_path = file_path
        self.zip_file_obj = zipfile.ZipFile(self.file_path, 'w')

    def build_readme(self, template, files_description, data_filter):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'helpfiles', template)
        with open(file_path, 'r') as input_file:
            content = input_file.read()
            content.replace('\n'.encode('utf-8'), '\r\n'.encode('utf-8'))
            content = content.replace('<put_filters_here>'.encode('utf-8'), data_filter.encode('utf-8'))
            content = content.replace('<put_additional_files_here>'.encode('utf-8'), files_description.encode('utf-8'))
        self.zip_file_obj.writestr(README_FILE_NAME, content)

    def write(self, file_path, arcname):
        self.zip_file_obj.write(file_path, arcname=arcname)

    def close(self):
        """ close zip file object """
        self.zip_file_obj.close()


class CSVHelper:
    """ csv builder helper """

    def __init__(self, es_client, es_query, index_name, chunk_size=5000, timeout=30):
        self.es_client = es_client
        self.es_query = es_query
        self.index_name = index_name
        self.chunk_size = 5000
        self.timeout = 30

        self.operator_dict = get_operator_list_for_select_input(to_dict=True)
        self.day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        self.timeperiod_dict = get_timeperiod_list_for_select_input(to_dict=True)
        self.halfhour_dict = get_halfhour_list_for_select_input(to_dict=True, format='name')
        self.commune_dict = get_commune_list_for_select_input(to_dict=True)

        self.translator = self.create_translator()

    def get_iterator(self, kwargs):
        es_query = Search(using=self.es_client, index=self.index_name).update_from_dict(self.es_query)
        es_query = es_query.source(self.get_fields())
        es_query.params = {'request_timeout': self.timeout, 'size': self.chunk_size}

        return es_query.scan()

    def download(self, zip_file_obj, **kwargs):
        tmp_file_name = str(uuid.uuid4())
        try:
            with open(tmp_file_name, 'wb') as output:
                writter = UnicodeWriter(output, delimiter=str(','))
                writter.writerow(self.get_header())

                for doc in self.get_iterator(kwargs):
                    row = self.row_parser(doc)
                    if isinstance(row[0], list):
                        # there are more than one row in variable
                        writter.writerows(row)
                    else:
                        writter.writerow(row)

            zip_file_obj.write(tmp_file_name, arcname=self.get_data_file_name())
        finally:
            os.remove(tmp_file_name)

    def get_column_dict(self):
        raise NotImplementedError()

    def create_translator(self):
        """ create dict with structure es_name: csv_name """
        return {x['es_name']: x['csv_name'] for x in self.get_column_dict()}

    def get_filter_criteria(self):
        """ return list used to put in readme file to specify filters applied over data """
        formatted_filters = []

        if 'bool' not in self.es_query['query']:
            return ''

        filters = self.es_query['query']['bool']['filter']

        if not isinstance(filters, list):
            raise FilterHasToBeListErrpr()

        for query_filter in filters:
            if 'term' in query_filter:
                field = query_filter['term'].keys()[0]
                value = query_filter['term'][field]
                field = field.split('.')[0]

                line = '\t\t- {0}: {1}'.format(self.translator[field], value)
                formatted_filters.append(line)
            elif 'terms' in query_filter:
                # ignore operator filter
                if 'operator' in query_filter['terms']:
                    continue
                field = query_filter['terms'].keys()[0]
                values = query_filter['terms'][field]

                if field == 'dayType':
                    values = [self.day_type_dict[int(x)] for x in values]
                elif field in ['timePeriodInStartTime', 'timePeriodInStopTime']:
                    values = [self.timeperiod_dict[int(x)] for x in values]
                elif field in ['halfHourInStartTime', 'halfHourInStopTime']:
                    values = [self.halfhour_dict[int(x)] for x in values]

                line = '\t\t- {0}:'.format(self.translator[field])
                formatted_filters.append(line)
                for value in values:
                    line = '\t\t\t{0}'.format(value)
                    formatted_filters.append(line)
            elif 'range' in query_filter:
                field = query_filter['range'].keys()[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")

                line = '\t\t- {0}: {1} - {2}'.format(self.translator[field], gte, lte)
                formatted_filters.append(line)

        return '{0}'.format(os.linesep).join(formatted_filters)

    def row_parser(self, row):
        raise NotImplementedError()

    def get_data_file_name(self):
        """ get data file name where will save main file """
        raise NotImplementedError()

    def get_header(self):
        """ get header of csv file """
        return map(lambda el: el['csv_name'], self.get_column_dict())

    def get_fields(self):
        """ get fields retrieved by query """
        return map(lambda el: el['es_name'], self.get_column_dict())

    def get_file_description(self):
        """ description to add to readme file """
        raise NotImplementedError()


class ProfileCSVHelper(CSVHelper):
    """ Class that represents a profile downloader. """

    def __init__(self, es_client, es_query):
        CSVHelper.__init__(self, es_client, es_query, ESProfileHelper().get_index_name())

    def get_column_dict(self):
        return [
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

    def get_data_file_name(self):
        return 'Perfil.csv'

    def get_file_description(self):
        description = 'archivo de perfiles de carga, cada fila representa el cruce de una expedición por una parada ' \
                      'de su secuencia de parada.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

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


class SpeedCSVHelper(CSVHelper):
    """ Class that represents a speed file. """

    def __init__(self, es_client, es_query):
        CSVHelper.__init__(self, es_client, es_query, ESSpeedHelper.get_index_name())

    def get_column_dict(self):
        return [
            {'es_name': 'operator', 'csv_name': 'Operador'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario'},
            {'es_name': 'section', 'csv_name': 'Identificador_tramo'},
            {'es_name': 'date', 'csv_name': 'Fecha_de_medición'},
            {'es_name': 'periodId', 'csv_name': 'Período_de_medición'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día'},
            {'es_name': 'totalDistance', 'csv_name': 'Distancia_total'},
            {'es_name': 'totalTime', 'csv_name': 'Tiempo_total'},
            {'es_name': 'speed', 'csv_name': 'Velocidad_m/s'},
            {'es_name': 'nObs', 'csv_name': 'Número_observaciones'},
            {'es_name': 'nInvalidObs', 'csv_name': 'Número_observaciones_inválidas'},
        ]

    def get_data_file_name(self):
        return 'Velocidad_tramos_500m.csv'

    def get_file_description(self):
        description = 'Cada línea representa la medición de la velocidad para un servicio cada 500 metros en ' \
                      'tramos horarios de media hora.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

    def row_parser(self, row):

        formatted_row = []
        for column_name in self.get_fields():
            value = row[column_name]
            try:
                if column_name == 'dayType':
                    value = self.day_type_dict[value]
                elif column_name == 'operator':
                    value = self.operator_dict[value]
            except KeyError:
                value = ""

            if isinstance(value, (int, float)):
                value = str(value)
            elif value is None:
                value = ""

            formatted_row.append(value)

        return formatted_row


class ODByRouteCSVHelper(CSVHelper):
    """ Class that represents a odbyroute file. """

    def __init__(self, es_client, es_query):
        CSVHelper.__init__(self, es_client, es_query, ESODByRouteHelper.get_index_name())

    def get_column_dict(self):
        return [
            {'es_name': 'date', 'csv_name': 'Fecha'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día'},
            {'es_name': 'operator', 'csv_name': 'Operador'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'timePeriodInStopTime', 'csv_name': 'Período_transantiago_subida'},
            {'es_name': 'startStopOrder', 'csv_name': 'Posición_parada_en_ruta_subida'},
            {'es_name': 'endStopOrder', 'csv_name': 'Posición_parada_en_ruta_bajada'},
            {'es_name': 'authStartStopCode', 'csv_name': 'Código_transantiago_parada_subida'},
            {'es_name': 'authEndStopCode', 'csv_name': 'Código_transantiago_parada_najada'},
            {'es_name': 'userStartStopCode', 'csv_name': 'Código_usuario_parada_subida'},
            {'es_name': 'userEndStopCode', 'csv_name': 'Código_usuario_parada_najda'},
            {'es_name': 'startStopName', 'csv_name': 'Nombre_parada_subida'},
            {'es_name': 'endStopName', 'csv_name': 'Nombre_parada_subida'},
            {'es_name': 'startZone', 'csv_name': 'Zona_777_subida'},
            {'es_name': 'endZone', 'csv_name': 'Zona_777_bajada'},
            {'es_name': 'tripNumber', 'csv_name': 'Número_etapas'},
            {'es_name': 'tripWithoutLanding', 'csv_name': 'Número_etapas_sin_bajada'},
            {'es_name': 'expandedTripNumber', 'csv_name': 'Número_etapas_expandido'},
        ]

    def get_data_file_name(self):
        return 'Matriz_etapas_por_servicio.csv'

    def get_file_description(self):
        description = 'Cada línea representa la cantidad de etapas realizadas entre dos paradas en un período ' \
                      'transantiago.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

    def row_parser(self, row):

        formatted_row = []
        for column_name in self.get_fields():
            value = row[column_name]
            try:
                if column_name == 'dayType':
                    value = self.day_type_dict[value]
                elif column_name == 'operator':
                    value = self.operator_dict[value]
                elif column_name == 'timePeriodInStopTime':
                    value = self.timeperiod_dict[value]
            except KeyError:
                value = ""

            if isinstance(value, (int, float)):
                value = str(value)
            elif value is None:
                value = ""

            formatted_row.append(value)

        return formatted_row


class TripCSVHelper(CSVHelper):
    """ Class that represents a odbyroute file. """

    def __init__(self, es_client, es_query):
        CSVHelper.__init__(self, es_client, es_query, ESTripHelper.get_index_name())

    def get_column_dict(self):
        return [
            {'es_name': 'id', 'csv_name': 'identificador_diario_viaje'},
            {'es_name': 'tipodia', 'csv_name': 'Tipo_día'},
            {'es_name': 'factor_expansion', 'csv_name': 'Factor_expansion'},
            {'es_name': 'n_etapas', 'csv_name': 'Número_etapas'},
            {'es_name': 'tviaje', 'csv_name': 'Tiempo_viaje'},
            {'es_name': 'distancia_eucl', 'csv_name': 'Distancia_euclidiana'},
            {'es_name': 'distancia_ruta', 'csv_name': 'Distancia_considerando_ruta'},
            {'es_name': 'tiempo_subida', 'csv_name': 'Tiempo_subida'},
            {'es_name': 'tiempo_bajada', 'csv_name': 'Tiempo_bajada'},
            {'es_name': 'mediahora_subida', 'csv_name': 'Media_hora_subida'},
            {'es_name': 'mediahora_bajada', 'csv_name': 'Media_hora_bajada'},
            {'es_name': 'periodo_subida', 'csv_name': 'Periodo_transantiago_subida'},
            {'es_name': 'periodo_bajada', 'csv_name': 'Período_transantiago_bajada'},
            {'es_name': 'tipo_transporte_1', 'csv_name': 'Tipo_transporte_etapa_1'},
            {'es_name': 'tipo_transporte_2', 'csv_name': 'Tipo_transporte_etapa_1'},
            {'es_name': 'tipo_transporte_3', 'csv_name': 'Tipo_transporte_etapa_1'},
            {'es_name': 'tipo_transporte_4', 'csv_name': 'Tipo_transporte_etapa_1'},
            {'es_name': 'srv_1', 'csv_name': 'Servicio_etapa_1'},
            {'es_name': 'srv_2', 'csv_name': 'Servicio_etapa_2'},
            {'es_name': 'srv_3', 'csv_name': 'Servicio_etapa_3'},
            {'es_name': 'srv_4', 'csv_name': 'Servicio_etapa_4'},
            {'es_name': 'paradero_subida', 'csv_name': 'Parada_subida'},
            {'es_name': 'paradero_bajada', 'csv_name': 'Parada_bajada'},
            {'es_name': 'comuna_subida', 'csv_name': 'Comuna_subida'},
            {'es_name': 'comuna_bajada', 'csv_name': 'Comuna_bajada'},
            {'es_name': 'zona_subida', 'csv_name': 'Zona_777_subida'},
            {'es_name': 'zona_bajada', 'csv_name': 'Zona_777_bajada'},
        ]

    def get_data_file_name(self):
        return 'Viajes.csv'

    def get_file_description(self):
        description = 'Cada línea representa un viaje.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

    def row_parser(self, row):

        formatted_row = []
        for column_name in self.get_fields():
            value = row[column_name]
            try:
                if column_name == 'tipodia':
                    value = self.day_type_dict[value]
                elif column_name in ['mediahora_subida', 'mediahora_bajada']:
                    value = self.halfhour_dict[value]
                elif column_name == ['periodo_subida', 'periodo_bajada']:
                    value = self.timeperiod_dict[value]
                elif column_name == ['tipo_transporte_1', 'tipo_transporte_2', 'tipo_transporte_3',
                                     'tipo_transporte_4']:
                    # TODO: apply dictionary
                    value = value
                elif column_name in ['comuna_subida', 'comuna_bajada']:
                    value = self.commune_dict[value]
            except KeyError:
                value = ""

            if isinstance(value, (int, float)):
                value = str(value)
            elif value is None:
                value = ""

            formatted_row.append(value)

        return formatted_row


class ShapeCSVHelper(CSVHelper):
    """ Class that represents a shape file. """

    def __init__(self, es_client):
        self.es_shape_helper = ESShapeHelper()
        CSVHelper.__init__(self, es_client, "", self.es_shape_helper.get_index_name())

    def get_column_dict(self):
        return [
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación'},
            {'es_name': 'points', 'csv_name': 'Latitud,Longitud,Inicio_segmento_500m'}
        ]

    def get_data_file_name(self):
        return 'Geometría_servicio.csv'

    def get_file_description(self):
        description = 'Geometría del servicio.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

    def get_iterator(self, kwargs):
        routes = kwargs['routes']
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']

        return [self.es_shape_helper.get_route_shape(route, start_date, end_date) for route in routes]

    def row_parser(self, row):
        rows = []

        route = row['route']
        start_date = row['startDate']
        points = row['points']

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


class StopCSVHelper(CSVHelper):
    """ Class that represents a stop file. """

    def __init__(self, es_client):
        self.es_stop_helper = ESStopHelper()
        CSVHelper.__init__(self, es_client, "", self.es_stop_helper.get_index_name())

    def get_column_dict(self):
        return [
            {'es_name': 'operator', 'csv_name': 'Operador'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación'},
            {'es_name': 'stops',
             'csv_name': 'Posición_en_ruta,Latitud,Longitud,Código_parada_transantiago,Código_parada_usuario,Nombre_parada'}
        ]

    def get_data_file_name(self):
        return 'Secuencia_paradas.csv'

    def get_file_description(self):
        description = 'paradas asignadas al servicio.'
        return '\t\t- {0}: {1}\r\n'.format(self.get_data_file_name(), description)

    def get_iterator(self, kwargs):
        routes = kwargs['routes']
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']

        return [self.es_stop_helper.get_stop_list(route, start_date, end_date) for route in routes]

    def row_parser(self, row):
        rows = []

        operator = self.operator_dict[row['operator']]
        auth_route_code = row['authRouteCode']
        user_route_code = row['userRouteCode']
        start_date = row['startDate']
        stops = row['stops']

        for stop in stops:
            stop_row = [
                operator,
                auth_route_code,
                user_route_code,
                start_date,
                str(stop['order']),
                str(stop['latitude']),
                str(stop['longitude']),
                stop['authStopCode'],
                stop['userStopCode'],
                stop['stopName'],
            ]
            rows.append(stop_row)

        return rows
