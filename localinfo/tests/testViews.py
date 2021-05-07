import json
import os
from unittest import mock

from django.urls import reverse

from localinfo.models import OPProgram
from testhelper.helper import TestHelper


class LocalInfoViewTest(TestHelper):
    fixtures = ['daytypes', 'operators', 'timeperioddates', 'timeperiods', 'halfhours', 'communes',
                'transportmodes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
        self.data = {
        }

    def test_OPDictionaryUploader_post(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        with open(os.path.join(self.path, 'diccionario_op_base.xlsx'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file, 'opId': op_program.id})
            self.assertEqual(200, response.status_code)
        op_program.delete()

    def test_OPDictionaryUploader_post_file_2(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        with open(os.path.join(self.path, 'diccionario_op_base.xlsx'), 'rb') as file:
            self.client.post(reverse('localinfo:opdictionaryupload'),
                             {'name': 'file.xlsx', 'OPDictionary': file, 'opId': op_program.id})
        with open(os.path.join(self.path, 'diccionario_op_base_2.xlsx'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file, 'opId': op_program.id})
            self.assertEqual(200, response.status_code)
        op_program.delete()

    def test_OPDictionaryUploader_post_file_error_empty(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')

        response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                    {'name': 'file.xlsx', 'OPDictionary': '', 'opId': op_program.id})
        self.assertEqual(400, response.status_code)
        self.assertEqual('No existe el archivo', json.loads(response.content)['error'])

    def test_OPDictionaryUploader_post_file_error_bad_file(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        with open(os.path.join(self.path, 'op_data.csv'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file, 'opId': op_program.id})
            self.assertEqual(400, response.status_code)
            self.assertEqual('Archivo en formato incorrecto', json.loads(response.content)['error'])

    def test_OPDictionaryUploader_post_file_error_wrong_format(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        with open(os.path.join(self.path, 'diccionario_op_base_error.xlsx'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file, 'opId': op_program.id})
            self.assertEqual(400, response.status_code)
            self.assertEqual('Archivo con datos en blanco', json.loads(response.content)['error'])

    def test_OPDictionaryUploader_post_file_error_empty_opId(self):
        with open(os.path.join(self.path, 'diccionario_op_base_error.xlsx'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file})
            self.assertEqual(400, response.status_code)
            self.assertEqual('Seleccione un programa de operación', json.loads(response.content)['error'])

    def test_OPDictionaryUploader_post_file_error_bad_opId(self):
        with open(os.path.join(self.path, 'diccionario_op_base_error.xlsx'), 'rb') as file:
            response = self.client.post(reverse('localinfo:opdictionaryupload'),
                                        {'name': 'file.xlsx', 'OPDictionary': file, 'opId': 0})
            self.assertEqual(400, response.status_code)
            self.assertEqual('Programa de operación no válido', json.loads(response.content)['error'])

    def test_TimePeriod_error(self):
        self.data['dates[]'] = ['2017-01-01', '2020-07-01']
        self.check_http_response(self.client, 'localinfo:timePeriod', 400, self.data)

    def test_TimePeriod(self):
        self.data['dates[]'] = ['2017-01-01', '2017-07-01']
        url = reverse('localinfo:timePeriod')
        response = self.client.get(url, self.data)
        expected_time_period = {
            'timePeriod': [
                {'value': 1, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
                {'value': 2, 'item': 'Nocturno (01:00:00-05:29:59)'},
                {'value': 3, 'item': 'Transición nocturno (05:30:00-06:29:59)'},
                {'value': 4, 'item': 'Punta mañana (06:30:00-08:29:59)'},
                {'value': 5, 'item': 'Transición punta mañana (08:30:00-09:29:59)'},
                {'value': 6, 'item': 'Fuera de punta mañana (09:30:00-12:29:59)'},
                {'value': 7, 'item': 'Punta mediodia (12:30:00-13:59:59)'},
                {'value': 8, 'item': 'Fuera de punta tarde (14:00:00-17:29:59)'},
                {'value': 9, 'item': 'Punta tarde (17:30:00-20:29:59)'},
                {'value': 10, 'item': 'Transición punta tarde (20:30:00-21:29:59)'},
                {'value': 11, 'item': 'Fuera de punta nocturno (21:30:00-22:59:59)'},
                {'value': 12, 'item': 'Pre nocturno (23:00:00-23:59:59)'},
                {'value': 13, 'item': 'Pre nocturno sábado (00:00:00-00:59:59)'},
                {'value': 14, 'item': 'Nocturno sábado (01:00:00-05:29:59)'},
                {'value': 15, 'item': 'Transición sábado mañana (05:30:00-06:29:59)'},
                {'value': 16, 'item': 'Punta mañana sábado (06:30:00-10:59:59)'},
                {'value': 17, 'item': 'Mañana sábado (11:00:00-13:29:59)'},
                {'value': 18, 'item': 'Punta mediodia sábado (13:30:00-17:29:59)'},
                {'value': 19, 'item': 'Tarde sábado (17:30:00-20:29:59)'},
                {'value': 20, 'item': 'Transición sábado nocturno (20:30:00-22:59:59)'},
                {'value': 21, 'item': 'Pre nocturno sábado (23:00:00-23:59:59)'},
                {'value': 22, 'item': 'Pre nocturno domingo (00:00:00-00:59:59)'},
                {'value': 23, 'item': 'Nocturno domingo (01:00:00-05:29:59)'},
                {'value': 24, 'item': 'Transición domingo mañana (05:30:00-09:29:59)'},
                {'value': 25, 'item': 'Mañana domingo (09:30:00-13:29:59)'},
                {'value': 26, 'item': 'Mediodia domingo (13:30:00-17:29:59)'},
                {'value': 27, 'item': 'Tarde domingo (17:30:00-20:59:59)'},
                {'value': 28, 'item': 'Transición domingo nocturno (21:00:00-22:59:59)'},
                {'value': 29, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}
            ]
        }
        self.assertEqual(expected_time_period, json.loads(response.content))
        self.assertEqual(200, response.status_code)

    def test_faq(self):
        self.check_http_response(self.client, 'localinfo:faq', 200)

    def test_faq_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_faq_changelist', 200)

    def test_opdictionary_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_opdictionary_changelist', 200)

    def test_calendarinfo_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_calendarinfo_changelist', 200)

    def test_daydescription_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_daydescription_changelist', 200)

    def test_halfhour_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_halfhour_changelist', 200)

    def test_operator_changelist(self):
        self.check_http_response(self.client, 'admin:localinfo_operator_changelist', 200)

    @mock.patch('localinfo.helper.ESOPDataHelper')
    def test_oppgram_selector_list(self, ESOPDataHelper):
        ESOPDataHelper.return_value.get_available_days.return_value = {}
        response = self.client.get(reverse('localinfo:opProgramList'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(json.loads(response.content)['opProgramList'])
