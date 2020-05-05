from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import helper


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestPaymentFactorCSVHelper(TestCase):

    def setUp(self):
        query = {'query': {'bool': {'filter': [{'terms': {'dayType': [u'day_type']}}, {'range': {
            'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-01||/d',
                     u'format': u'yyyy-MM-dd'}}}]}}, 'from': 0, 'aggs': {
            u'by_bus_station_id': {'terms': {'field': u'busStationId', 'size': 10000}, 'aggs': {
                u'by_bus_station_name': {'terms': {'field': u'busStationName'}, 'aggs': {
                    u'by_assignation': {'terms': {'field': u'assignation'}, 'aggs': {
                        u'by_operator': {'terms': {'field': u'operator'}, 'aggs': {
                            u'by_day_type': {'terms': {'field': u'dayType'}, 'aggs': {
                                u'by_date': {'terms': {'field': u'date', 'size': 10000},
                                             'aggs': {u'factor': {'sum': {'field': u'factor'}}}},
                                u'sum': {'sum': {'field': u'sum'}}, u'total': {'sum': {'field': u'total'}},
                                u'neutral': {'sum': {'field': u'neutral'}},
                                u'subtraction': {'sum': {'field': u'subtraction'}}}}}}}}}}}}}, 'size': 0}

        self.csv_helper = helper.PaymentFactorCSVHelper(None, query)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Distribución_de_validaciones.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'date', 'csv_name': 'Fecha', 'definition': 'Día en que se realizaron las validaciones'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día'},
            {'es_name': 'operator', 'csv_name': 'Id Operador',
             'definition': 'Identificador de empresa asociada a la zona paga'},
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa asociada a la zona paga'},
            {'es_name': 'assignation', 'csv_name': 'Asignación',
             'definition': 'Indica si el operador está asignado a la zona paga'},
            {'es_name': 'busStationId', 'csv_name': 'Identificador_zona_paga',
             'definition': 'Código que identifica la zona paga'},
            {'es_name': 'busStationName', 'csv_name': 'Nombre_zona_paga',
             'definition': 'Nombre de la parada donde se encuentra la zona paga'},
            {'es_name': 'total', 'csv_name': 'Total', 'definition': ''},
            {'es_name': 'sum', 'csv_name': 'Suman', 'definition': ''},
            {'es_name': 'subtraction', 'csv_name': 'Restan', 'definition': ''},
            {'es_name': 'neutral', 'csv_name': 'Neutras', 'definition': ''},
            {'es_name': 'factor', 'csv_name': 'Factor', 'definition': 'Factor de pago'},
            {'es_name': 'routes', 'csv_name': 'Servicios',
             'definition': 'Servicios que se detienen en esta parada, separados por el signo "-"'},
            {'es_name': 'transactions', 'csv_name': 'Validaciones',
             'definition': 'N° de validaciones por servicio, están separados por el signo "-" y su servicio asociado es el ubicado en la misma posición de la columna "Servicios"'},
            {'es_name': 'validatorId', 'csv_name': 'Id de validador',
             'definition': 'Identificador del validador asociado a la zona paga'},
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Distribución_de_validaciones.csv: Cada línea representa las validaciones asociadas a un operador en una zona paga\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestStopByRouteCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.StopByRouteCSVHelper(None)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Secuencia_paradas.csv")

    def test_get_column_dict(self):
        expected = [
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
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Secuencia_paradas.csv: paradas asignadas al servicio.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestPaymentFactorCSVHelper(TestCase):

    def setUp(self):
        query = {'query': {'bool': {'filter': [{'terms': {'dayType': [u'day_type']}}, {'range': {
            'date': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-01||/d',
                     u'format': u'yyyy-MM-dd'}}}]}}, 'from': 0, 'aggs': {
            u'by_bus_station_id': {'terms': {'field': u'busStationId', 'size': 10000}, 'aggs': {
                u'by_bus_station_name': {'terms': {'field': u'busStationName'}, 'aggs': {
                    u'by_assignation': {'terms': {'field': u'assignation'}, 'aggs': {
                        u'by_operator': {'terms': {'field': u'operator'}, 'aggs': {
                            u'by_day_type': {'terms': {'field': u'dayType'}, 'aggs': {
                                u'by_date': {'terms': {'field': u'date', 'size': 10000},
                                             'aggs': {u'factor': {'sum': {'field': u'factor'}}}},
                                u'sum': {'sum': {'field': u'sum'}}, u'total': {'sum': {'field': u'total'}},
                                u'neutral': {'sum': {'field': u'neutral'}},
                                u'subtraction': {'sum': {'field': u'subtraction'}}}}}}}}}}}}}, 'size': 0}

        self.csv_helper = helper.PaymentFactorCSVHelper(None, query)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Distribución_de_validaciones.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'date', 'csv_name': 'Fecha', 'definition': 'Día en que se realizaron las validaciones'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día'},
            {'es_name': 'operator', 'csv_name': 'Id Operador',
             'definition': 'Identificador de empresa asociada a la zona paga'},
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa asociada a la zona paga'},
            {'es_name': 'assignation', 'csv_name': 'Asignación',
             'definition': 'Indica si el operador está asignado a la zona paga'},
            {'es_name': 'busStationId', 'csv_name': 'Identificador_zona_paga',
             'definition': 'Código que identifica la zona paga'},
            {'es_name': 'busStationName', 'csv_name': 'Nombre_zona_paga',
             'definition': 'Nombre de la parada donde se encuentra la zona paga'},
            {'es_name': 'total', 'csv_name': 'Total', 'definition': ''},
            {'es_name': 'sum', 'csv_name': 'Suman', 'definition': ''},
            {'es_name': 'subtraction', 'csv_name': 'Restan', 'definition': ''},
            {'es_name': 'neutral', 'csv_name': 'Neutras', 'definition': ''},
            {'es_name': 'factor', 'csv_name': 'Factor', 'definition': 'Factor de pago'},
            {'es_name': 'routes', 'csv_name': 'Servicios',
             'definition': 'Servicios que se detienen en esta parada, separados por el signo "-"'},
            {'es_name': 'transactions', 'csv_name': 'Validaciones',
             'definition': 'N° de validaciones por servicio, están separados por el signo "-" y su servicio asociado es el ubicado en la misma posición de la columna "Servicios"'},
            {'es_name': 'validatorId', 'csv_name': 'Id de validador',
             'definition': 'Identificador del validador asociado a la zona paga'},
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Distribución_de_validaciones.csv: Cada línea representa las validaciones asociadas a un operador en una zona paga\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestBipCSVHelper(TestCase):

    def setUp(self):
        query = {'query': {'bool': {'filter': [{'terms': {'operator': [0]}}, {'range': {
            'validationTime': {u'time_zone': u'+00:00', u'gte': u'2018-01-01||/d', u'lte': u'2018-01-01||/d',
                               u'format': u'yyyy-MM-dd'}}}]}}, 'aggs': {
            u'histogram': {'date_histogram': {'field': u'validationTime', 'interval': u'day'},
                           'aggs': {u'operators': {'terms': {'field': u'operator', 'size': 1000}}}}}}

        self.csv_helper = helper.BipCSVHelper(None, query)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Bip.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código de transantiago del servicio'},
            {'es_name': 'userRoute', 'csv_name': 'Servicio_usuario',
             'definition': 'Código de usuario del servicio (ejemplo: 506)'},
            {'es_name': 'validationTime', 'csv_name': 'Hora_validacion',
             'definition': 'Fecha y hora de la validación'},
            {'es_name': 'bipNumber', 'csv_name': 'Número Bip', 'definition': 'Número de la tarjeta bip'},
            {'es_name': 'source', 'csv_name': 'Fuente de dato',
             'definition': 'Bus, estación de metro, metrobus o totem validador.'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Bip.csv: archivo de transacciones bip, cada fila representa una validación bip\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())
