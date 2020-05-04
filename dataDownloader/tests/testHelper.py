from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import helper


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
