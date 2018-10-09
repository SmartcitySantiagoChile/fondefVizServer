# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search

from rqworkers.dataDownloader.unicodecsv import UnicodeWriter
from rqworkers.dataDownloader.errors import FilterHasToBeListError

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_operator_list_for_select_input, get_halfhour_list_for_select_input, get_commune_list_for_select_input, \
    get_transport_mode_list_for_select_input

from esapi.helper.profile import ESProfileHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
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
SPEED_MATRIX_DATA = 'speed_matrix_data'
TRIP_DATA = 'trip_data'


class WrongFormatterError(Exception):
    pass


class ZipManager:
    """ to manage zip file """

    def __init__(self, file_path):
        self.file_path = file_path
        self.zip_file_obj = zipfile.ZipFile(self.file_path, mode='w', compression=zipfile.ZIP_DEFLATED)

    def build_readme(self, file_title, files_description, data_filter, field_explanation):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'helptemplate', 'template.readme')
        with open(file_path, 'r') as input_file:
            content = input_file.read()
            content = content.replace('<put_title_here>'.encode('utf-8'), file_title.encode('utf-8'))
            content = content.replace('<put_filters_here>'.encode('utf-8'), data_filter.encode('utf-8'))
            content = content.replace('<put_file_description_here>'.encode('utf-8'), files_description.encode('utf-8'))
            content = content.replace('<put_field_explanation_here>'.encode('utf-8'), field_explanation.encode('utf-8'))
        self.zip_file_obj.writestr(README_FILE_NAME, content)

    def write(self, file_path, arcname):
        self.zip_file_obj.write(file_path, arcname=arcname)

    def close(self):
        """ close zip file object """
        self.zip_file_obj.close()


class CSVHelper:
    """ csv builder helper """
    FORMATTER_FOR_WEB = 'for_web'
    FORMATTER_FOR_FILE = 'for_file'

    def __init__(self, es_client, es_query, index_name):
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
        self.transport_mode_dict = get_transport_mode_list_for_select_input(to_dict=True)

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

    def get_field_explanation(self):
        explanation = 'El archivo {0} contiene las siguientes columnas:\r\n'.format(self.get_data_file_name())
        explanation += "\r\n".join(['\t- \'{0}\': {1}'.format(field['csv_name'], field['definition']) for field in
                                    self.get_column_dict()])
        return explanation

    def _process_filters(self, filters):
        formatted_filters = []

        for query_filter in filters:
            if 'term' in query_filter:
                field = query_filter['term'].keys()[0]
                value = query_filter['term'][field]
                field = field.split('.')[0]

                attr_filter = {
                    'field': self.translator[field],
                    'value': value
                }
                formatted_filters.append(attr_filter)
            elif 'terms' in query_filter:
                # ignore operator filter
                if 'operator' in query_filter['terms']:
                    continue
                field = query_filter['terms'].keys()[0]
                values = query_filter['terms'][field]

                if field in ['dayType', 'tipodia']:
                    values = [self.day_type_dict[int(x)] for x in values]
                elif field in ['timePeriodInStartTime', 'timePeriodInStopTime', 'periodo_bajada_1',
                               'periodo_bajada_2', 'periodo_bajada_3', 'periodo_bajada_4']:
                    values = [self.timeperiod_dict[int(x)] for x in values]
                elif field in ['halfHourInStartTime', 'halfHourInStopTime', 'mediahora_bajada_1',
                               'mediahora_bajada_2', 'mediahora_bajada_3', 'mediahora_bajada_4']:
                    values = [self.halfhour_dict[int(x)] for x in values]

                formatted_values = []
                for value in values:
                    formatted_values.append(value)

                attr_filter = {
                    'field': self.translator[field],
                    'value': formatted_values
                }
                formatted_filters.append(attr_filter)
            elif 'range' in query_filter:
                field = query_filter['range'].keys()[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")

                attr_filter = {
                    'field': self.translator[field],
                    'value': 'entre {0} 00:00:00 y {1} 23:59:59'.format(gte, lte)
                }
                formatted_filters.append(attr_filter)
            elif 'bool' in query_filter:
                nested_filters = query_filter['bool']['should']
                attr_filter = {
                    'group': True,
                    'field': '',
                    'value': self._process_filters(nested_filters)
                }
                formatted_filters.append(attr_filter)
            elif 'must' in query_filter:
                nested_filters = query_filter['must'][0]['term']
                raw_field = nested_filters.keys()[0]
                field = nested_filters.keys()[0].split('.')[0]
                attr_filter = {
                    'field': self.translator[field],
                    'value': nested_filters[raw_field]
                }
                formatted_filters.append(attr_filter)

        return formatted_filters

    def _formatter_for_web(self, elements, sep=' y '):
        break_line = '<br />'
        description = ''
        for element in elements:
            if 'group' in element:
                description += '{0}({1})'.format(sep, self._formatter_for_web(element['value'], ' o '))
            else:
                value = element['value']
                if isinstance(value, list):
                    value = ' o '.join(value)
                description += '{0}{1}: {2}{3}'.format(sep, element['field'], value, break_line)

        return description[2:]

    def _formatter_for_file(self, elements, sep='\t- ', break_line='\r\n', cut_first_letters=False):
        description = ''
        for element in elements:
            if 'group' in element:
                description += '{0}({1}){2}'.format(sep, self._formatter_for_file(element['value'], ' o ', '', True), break_line)
            else:
                value = element['value']
                if isinstance(value, list):
                    value = ' o '.join(value)
                description += '{0}{1}: {2}{3}'.format(sep, element['field'], value, break_line)

        return description if not cut_first_letters else description[3:]

    def get_filter_criteria(self, formatter):
        """ return list used to put in readme file to specify filters applied over data """

        if 'bool' not in self.es_query['query']:
            return ''

        filter_list = []
        for bool_filter in self.es_query['query']['bool']:
            bool_filter_list = self.es_query['query']['bool'][bool_filter]
            if not isinstance(bool_filter_list, list):
                raise FilterHasToBeListError()
            filter_list += self._process_filters(bool_filter_list)

        if formatter == self.FORMATTER_FOR_FILE:
            return self._formatter_for_file(filter_list)
        elif formatter == self.FORMATTER_FOR_WEB:
            return self._formatter_for_web(filter_list)
        else:
            raise WrongFormatterError()

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
        CSVHelper.__init__(self, es_client, es_query, ESProfileHelper().index_name)

    def get_column_dict(self):
        return [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código de transantiago del servicio'},
            {'es_name': 'userRoute', 'csv_name': 'Servicio_usuario',
             'definition': 'Código de usuario del servicio (ejemplo: 506)'},
            {'es_name': 'licensePlate', 'csv_name': 'Patente',
             'definition': 'Patente de la máquina que realizó la expedición'},
            {'es_name': 'authStopCode', 'csv_name': 'Código_parada_transantiago',
             'definition': 'Código de transantiago de la parada por la que pasó el servicio'},
            {'es_name': 'userStopCode', 'csv_name': 'Código_parada_usuario',
             'definition': 'Código de usuario de la parada por la que pasó el servicio (ejemplo: PA433)'},
            {'es_name': 'userStopName', 'csv_name': 'Nombre_parada',
             'definition': 'Nombre de la parada por la que pasó el servicio'},
            {'es_name': 'expeditionStartTime', 'csv_name': 'Hora_inicio_expedición',
             'definition': 'Fecha y hora de inicio de la expedición'},
            {'es_name': 'expeditionEndTime', 'csv_name': 'Hora_fin_expedición',
             'definition': 'Fecha y hora de fin de la expedición'},
            {'es_name': 'fulfillment', 'csv_name': 'Cumplimiento', 'definition': ''},
            {'es_name': 'expeditionStopOrder', 'csv_name': 'Secuencia_parada',
             'definition': 'Posición de la parada dentro de la secuencia de paradas asociada al servicio'},
            {'es_name': 'expeditionDayId', 'csv_name': 'Identificador_expedición_día',
             'definition': 'identificador de la expedición, es único dentro del día'},
            {'es_name': 'stopDistanceFromPathStart', 'csv_name': 'Distancia_parada_desde_inicio_ruta',
             'definition': 'Distancia en metros entre el inicio de la ruta del servicio y la parada, considera la geometría de la ruta (no es euclidiana)'},
            {'es_name': 'expandedBoarding', 'csv_name': 'Subidas_expandidas',
             'definition': 'Número de personas que subieron al bus en la parada'},
            {'es_name': 'expandedAlighting', 'csv_name': 'Bajadas_expandidas',
             'definition': 'Número de personas que bajaron del bus en la parada'},
            {'es_name': 'loadProfile', 'csv_name': 'Perfil_carga_al_llegar',
             'definition': 'Número de personas arriba del bus al llegar a la parada'},
            {'es_name': 'busCapacity', 'csv_name': 'Capacidad_bus',
             'definition': 'Número máximo de personas que pueden estar dentro del bus'},
            {'es_name': 'expeditionStopTime', 'csv_name': 'Hora_en_parada',
             'definition': 'Fecha y hora en que la máquina pasó por la parada'},
            {'es_name': 'timePeriodInStartTime', 'csv_name': 'Periodo_transantiago_inicio_expedicion',
             'definition': 'Período transantiago en que inició la expedición'},
            {'es_name': 'timePeriodInStopTime', 'csv_name': 'Periodo_transantiago_parada_expedición',
             'definition': 'Período transantiago en que finalizó la expedición'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_dia',
             'definition': 'Tipo de día considerado por adatrap al momento de realizar el procesamiento de los datos'},
            {'es_name': 'busStation', 'csv_name': 'Zona_paga',
             'definition': 'Indica si la parada es zona paga (1: es zona paga, 0: no es zona paga)'},
            {'es_name': 'transactions', 'csv_name': 'Número_transacciones_en_parada',
             'definition': 'Número de transacciones realizadas en el paradero'},
            {'es_name': 'halfHourInStartTime', 'csv_name': 'Media_hora_de_inicio_expedición',
             'definition': 'Indica el período de media hora que la expedición inicio el recorrido (ejemplo: 16:00:00)'},
            {'es_name': 'halfHourInStopTime', 'csv_name': 'Media_hora_en_parada',
             'definition': 'Indica el período de media hora que la expedición pasó por la parada (ejemplo: 16:00:00)'},
            {'es_name': 'notValid', 'csv_name': 'Expedición_inválida',
             'definition': 'indica si la expedición contiene alguno de los siguientes problemas -> porcentaje de paraderos con carga menor a -1 es superior al 1% o porcentaje de paraderos con carga mayor al 1% sobre la capacidad del bus es superior al 1%'}
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
        CSVHelper.__init__(self, es_client, es_query, ESSpeedHelper().index_name)

    def get_column_dict(self):
        return [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'section', 'csv_name': 'Identificador_tramo',
             'definition': 'Identificador del tramo de 500 metros (ejemplo: tramo 3 corresponde a la sección [1.500, 2.000] de la ruta del servicio)'},
            {'es_name': 'date', 'csv_name': 'Fecha_de_medición', 'definition': 'Fecha de la medición'},
            {'es_name': 'periodId', 'csv_name': 'Período_de_medición',
             'definition': 'Período de media hora de la medición'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día en que se realizó la medicion'},
            {'es_name': 'totalDistance', 'csv_name': 'Distancia_total',
             'definition': 'Distancia recorrida por las expediciones que cruzaron en el tramo en el período de medición'},
            {'es_name': 'totalTime', 'csv_name': 'Tiempo_total',
             'definition': 'Tiempo usado por las expediciones que cruzaron el tramo en el período de medición'},
            {'es_name': 'speed', 'csv_name': 'Velocidad_m/s', 'definition': 'Velocidad del tramo, período'},
            {'es_name': 'nObs', 'csv_name': 'Número_observaciones',
             'definition': 'Número de puntos gps utilizados para realizar el cálculo de la velocidad'},
            {'es_name': 'nInvalidObs', 'csv_name': 'Número_observaciones_inválidas',
             'definition': 'Número de observaciones no usadas'}
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
        CSVHelper.__init__(self, es_client, es_query, ESODByRouteHelper().index_name)

    def get_column_dict(self):
        return [
            {'es_name': 'date', 'csv_name': 'Fecha', 'definition': 'Día en que inició la etapa'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día en que inició la etapa'},
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'timePeriodInStopTime', 'csv_name': 'Período_transantiago_subida',
             'definition': 'Período transantiago en que la expedición pasó por la parada'},
            {'es_name': 'startStopOrder', 'csv_name': 'Posición_parada_en_ruta_subida',
             'definition': 'Posición de la parada de subida en la ruta del servicio'},
            {'es_name': 'endStopOrder', 'csv_name': 'Posición_parada_en_ruta_bajada',
             'definition': 'Posición de la parada de bajada en la ruta del servicio'},
            {'es_name': 'authStartStopCode', 'csv_name': 'Código_transantiago_parada_subida',
             'definition': 'Código transantiago de la parada de subida'},
            {'es_name': 'authEndStopCode', 'csv_name': 'Código_transantiago_parada_bajada',
             'definition': 'Código transantiago de la parada de bajada'},
            {'es_name': 'userStartStopCode', 'csv_name': 'Código_usuario_parada_subida',
             'definition': 'Código usuario de la parada de subida'},
            {'es_name': 'userEndStopCode', 'csv_name': 'Código_usuario_parada_bajada',
             'definition': 'Código usuario de la parada de bajada'},
            {'es_name': 'startStopName', 'csv_name': 'Nombre_parada_subida',
             'definition': 'Nombre de la parada de subida'},
            {'es_name': 'endStopName', 'csv_name': 'Nombre_parada_subida',
             'definition': 'Nombre de la parada de bajada'},
            {'es_name': 'startZone', 'csv_name': 'Zona_777_subida',
             'definition': 'Zona 777 asociada a la parada de subida'},
            {'es_name': 'endZone', 'csv_name': 'Zona_777_bajada',
             'definition': 'Zona 777 asociada a la parada de bajada'},
            {'es_name': 'tripNumber', 'csv_name': 'Número_etapas',
             'definition': 'Número de usuarios que realizó la etapa'},
            {'es_name': 'tripWithoutLanding', 'csv_name': 'Número_etapas_sin_bajada',
             'definition': 'Número de etapas sin bajada'},
            {'es_name': 'expandedTripNumber', 'csv_name': 'Número_etapas_expandido',
             'definition': 'Número de etapas expandido'}
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
        CSVHelper.__init__(self, es_client, es_query, ESTripHelper().index_name)

    def get_column_dict(self):
        return [
            {'es_name': 'tipodia', 'csv_name': 'Tipo_día', 'definition': 'tipo de día en el que inició el viaje'},
            {'es_name': 'factor_expansion', 'csv_name': 'Factor_expansion',
             'definition': 'Factor de expansión asociado al viaje'},
            {'es_name': 'n_etapas', 'csv_name': 'Número_etapas',
             'definition': 'Número de etapas que constituyen el viaje'},
            {'es_name': 'tviaje', 'csv_name': 'Tiempo_viaje', 'definition': 'Duración del viaje en segundos'},
            {'es_name': 'distancia_eucl', 'csv_name': 'Distancia_euclidiana',
             'definition': 'Distancia euclidiana del viaje'},
            {'es_name': 'distancia_ruta', 'csv_name': 'Distancia_considerando_ruta',
             'definition': 'distancia considerando la ruta de los modos utilizados durante el viaje'},
            {'es_name': 'tiempo_subida', 'csv_name': 'Tiempo_subida', 'definition': 'Fecha y hora en que se inició el viaje'},
            {'es_name': 'tiempo_bajada', 'csv_name': 'Tiempo_bajada', 'definition': 'Fecha y hora en que terminó el viaje'},
            {'es_name': 'mediahora_subida', 'csv_name': 'Media_hora_subida', 'definition': 'Tramo de media hora en que inició el viaje'},
            {'es_name': 'mediahora_bajada', 'csv_name': 'Media_hora_bajada', 'definition': 'Tramo de media hora en que finalizó el viaje'},
            {'es_name': 'periodo_subida', 'csv_name': 'Periodo_transantiago_subida', 'definition': 'Período transantiago en que inició el viaje'},
            {'es_name': 'periodo_bajada', 'csv_name': 'Período_transantiago_bajada', 'definition': 'Período transantiago en que finalizó el viaje'},
            {'es_name': 'tipo_transporte_1', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 1'},
            {'es_name': 'tipo_transporte_2', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 2'},
            {'es_name': 'tipo_transporte_3', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 3'},
            {'es_name': 'tipo_transporte_4', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 4'},
            {'es_name': 'srv_1', 'csv_name': 'Servicio_etapa_1', 'definition': 'Servicio utilizado en la etapa 1'},
            {'es_name': 'srv_2', 'csv_name': 'Servicio_etapa_2', 'definition': 'Servicio utilizado en la etapa 2'},
            {'es_name': 'srv_3', 'csv_name': 'Servicio_etapa_3', 'definition': 'Servicio utilizado en la etapa 3'},
            {'es_name': 'srv_4', 'csv_name': 'Servicio_etapa_4', 'definition': 'Servicio utilizado en la etapa 4'},
            {'es_name': 'paradero_subida', 'csv_name': 'Parada_subida', 'definition': 'Código transantiago de la parada donde inició el viaje'},
            {'es_name': 'paradero_bajada', 'csv_name': 'Parada_bajada', 'definition': 'Código transantiago de la parada donde finalizó el viaje'},
            {'es_name': 'comuna_subida', 'csv_name': 'Comuna_subida',
             'definition': 'Comuna asociada a la parada de subida de la primera etapa del viaje'},
            {'es_name': 'comuna_bajada', 'csv_name': 'Comuna_bajada',
             'definition': 'Comuna asociada a la parada de bajada de la última etapa del viaje'},
            {'es_name': 'zona_subida', 'csv_name': 'Zona_777_subida',
             'definition': 'Zona 777 asociada a la subida de la etapa 1 del viaje'},
            {'es_name': 'zona_bajada', 'csv_name': 'Zona_777_bajada',
             'definition': 'Zona 777 asociada a la bajada de la última etapa del viaje'},
            {'es_name': 'modos', 'csv_name': 'Modo_viajes',
             'definition': 'Modos de transporte utilizados en el viaje (resumen)'},
            {'es_name': 'zona_subida_1', 'csv_name': 'Zona_subidad_etapa_1',
             'definition': 'Zona 777 asociada a la subida de la etapa 1'},
            {'es_name': 'zona_bajada_1', 'csv_name': 'Zona_bajada_etapa_1',
             'definition': 'Zona 777 asociada a la bajada de la etapa 1'},
            {'es_name': 'zona_subida_2', 'csv_name': 'Zona_subidad_etapa_2',
             'definition': 'Zona 777 asociada a la subida de la etapa 2'},
            {'es_name': 'zona_bajada_2', 'csv_name': 'Zona_bajada_etapa_2',
             'definition': 'Zona 777 asociada a la bajada de la etapa 2'},
            {'es_name': 'zona_subida_3', 'csv_name': 'Zona_subidad_etapa_3',
             'definition': 'Zona 777 asociada a la subida de la etapa 3'},
            {'es_name': 'zona_bajada_3', 'csv_name': 'Zona_bajada_etapa_3',
             'definition': 'Zona 777 asociada a la bajada de la etapa 3'},
            {'es_name': 'zona_subida_4', 'csv_name': 'Zona_subidad_etapa_4',
             'definition': 'Zona 777 asociada a la subida de la etapa 4'},
            {'es_name': 'zona_bajada_4', 'csv_name': 'Zona_bajada_etapa_4',
             'definition': 'Zona 777 asociada a la bajada de la etapa 4'},
            {'es_name': 'mediahora_bajada_1', 'csv_name': 'mediahora_bajada_etapa_1',
             'definition': 'Media hora de la bajada asociada a la etapa 1'},
            {'es_name': 'mediahora_bajada_2', 'csv_name': 'mediahora_bajada_etapa_2',
             'definition': 'Media hora de la bajada asociada a la etapa 2'},
            {'es_name': 'mediahora_bajada_3', 'csv_name': 'mediahora_bajada_etapa_3',
             'definition': 'Media hora de la bajada asociada a la etapa 3'},
            {'es_name': 'mediahora_bajada_4', 'csv_name': 'mediahora_bajada_etapa_4',
             'definition': 'Media hora de la bajada asociada a la etapa 4'},
            {'es_name': 'parada_subida_1', 'csv_name': 'parada_subida_1', 'definition': 'Código transantiago de la parada donde inició la etapa 1'},
            {'es_name': 'parada_subida_2', 'csv_name': 'parada_subida_2', 'definition': 'Código transantiago de la parada donde inició la etapa 2'},
            {'es_name': 'parada_subida_3', 'csv_name': 'parada_subida_3', 'definition': 'Código transantiago de la parada donde inició la etapa 3'},
            {'es_name': 'parada_subida_4', 'csv_name': 'parada_subida_4', 'definition': 'Código transantiago de la parada donde inició la etapa 4'},
            {'es_name': 'parada_bajada_1', 'csv_name': 'parada_bajada_1', 'definition': 'Código transantiago de la parada donde terminó la etapa 1'},
            {'es_name': 'parada_bajada_2', 'csv_name': 'parada_bajada_2', 'definition': 'Código transantiago de la parada donde terminó la etapa 2'},
            {'es_name': 'parada_bajada_3', 'csv_name': 'parada_bajada_3', 'definition': 'Código transantiago de la parada donde terminó la etapa 3'},
            {'es_name': 'parada_bajada_4', 'csv_name': 'parada_bajada_4', 'definition': 'Código transantiago de la parada donde terminó la etapa 4'},
            {'es_name': 'periodo_bajada_1', 'csv_name': 'periodo_bajada_etapa_1',
             'definition': 'Período transantiago de bajada asociada a la etapa 1'},
            {'es_name': 'periodo_bajada_2', 'csv_name': 'periodo_bajada_etapa_2',
             'definition': 'Período transantiago de bajada asociada a la etapa 2'},
            {'es_name': 'periodo_bajada_3', 'csv_name': 'periodo_bajada_etapa_3',
             'definition': 'Período transantiago de bajada asociada a la etapa 3'},
            {'es_name': 'periodo_bajada_4', 'csv_name': 'periodo_bajada_etapa_4',
             'definition': 'Período transantiago de bajada asociada a la etapa 4'}
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
                elif column_name in ['mediahora_subida', 'mediahora_bajada', 'mediahora_bajada_1', 'mediahora_bajada_2',
                                     'mediahora_bajada_3', 'mediahora_bajada_4']:
                    value = self.halfhour_dict[value]
                elif column_name in ['periodo_subida', 'periodo_bajada', 'periodo_bajada_1', 'periodo_bajada_2',
                                     'periodo_bajada_3', 'periodo_bajada_4']:
                    value = self.timeperiod_dict[value]
                elif column_name in ['tipo_transporte_1', 'tipo_transporte_2', 'tipo_transporte_3',
                                     'tipo_transporte_4']:
                    if value == 3:
                        value = "Zona paga"
                    else:
                        value = self.transport_mode_dict[value]
                elif column_name in ['modos']:
                    value = self.transport_mode_dict[value]
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
        CSVHelper.__init__(self, es_client, "", self.es_shape_helper.index_name)

    def get_column_dict(self):
        """ this class uses this just to build csv header """
        return [
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago', 'definition': 'Código transantiago del servicio'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación',
             'definition': 'Fecha de inicio del programa de operación desde el que esta geometría es válida'},
            {'es_name': '', 'csv_name': 'Latitud', 'definition': 'Latitud'},
            {'es_name': '', 'csv_name': 'Longitud', 'definition': 'Longitud'},
            {'es_name': '', 'csv_name': 'Inicio_segmento_500m',
             'definition': 'Indica si el punto corresponde al inicio de un tramo de 500 metros (1: si, 0: no)'}
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

        route = row['authRouteCode']
        start_date = row['startDate'][:10]
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


class StopByRouteCSVHelper(CSVHelper):
    """ Class that represents a stop file. """

    def __init__(self, es_client):
        self.es_stop_helper = ESStopByRouteHelper()
        CSVHelper.__init__(self, es_client, "", self.es_stop_helper.index_name)

    def get_column_dict(self):
        """ this class uses this just to build csv header """
        return [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación',
             'definition': 'Fecha de inicio del programa de operación desde el que esta ruta es válida'},
            {'es_name': '', 'csv_name': 'Posición_en_ruta',
             'definition': 'Posición de la parada dentro de la secuencia de paradas del servicio'},
            {'es_name': '', 'csv_name': 'Latitud', 'definition': 'Latitud'},
            {'es_name': '', 'csv_name': 'Longitud', 'definition': 'longitud'},
            {'es_name': '', 'csv_name': 'Código_parada_transantiago', 'definition': 'Código transantiago de la parada'},
            {'es_name': '', 'csv_name': 'Código_parada_usuario', 'definition': 'Código usuario de la parada'},
            {'es_name': '', 'csv_name': 'Nombre_parada', 'definition': 'Nombre de la parada'}
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
        start_date = row['startDate'][:10]
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
