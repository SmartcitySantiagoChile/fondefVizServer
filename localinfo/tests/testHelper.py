import os
from datetime import datetime
from unittest import mock

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from django.utils import timezone

from localinfo.helper import get_op_route, get_op_routes_dict, _list_parser, _dict_parser, \
    get_day_type_list_for_select_input, get_operator_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_halfhour_list_for_select_input, get_commune_list_for_select_input, get_transport_mode_list_for_select_input, \
    get_calendar_info, get_all_faqs, search_faq, get_valid_time_period_date, get_periods_dict, synchronize_op_program, \
    get_opprogram_list_for_select_input, upload_csv_op_dictionary, check_period_list_id
from localinfo.models import DayDescription, CalendarInfo, OPDictionary, FAQ, OPProgram


class TestHelperUtils(TestCase):
    fixtures = ['daytypes', 'operators', 'timeperioddates', 'timeperiods', 'halfhours', 'communes', 'transportmodes']

    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
        self.test_faq = FAQ(question='¿Es esta una pregunta de prueba?', answer='Siempre lo fue', category='route')
        self.test_faq.save()

    def test_get_custom_routes_dict(self):
        valid_from = '2020-01-01'
        expected_dict = {valid_from: {'T101 00I': ['101 Ida'], 'T101 00R': ['101 Regreso'], 'T112 00I': ['112 Ida']}}
        time_at = timezone.now()
        op_program = OPProgram.objects.create(valid_from=valid_from)
        for key in expected_dict[valid_from]:
            OPDictionary.objects.create(auth_route_code=key, route_type=expected_dict[valid_from][key][0],
                                        op_route_code=key, user_route_code=key, created_at=time_at,
                                        op_program=op_program)
        query = get_op_routes_dict()
        self.assertEqual(expected_dict, query)
        op_program.delete()

    def test_get_op_route(self):
        auth_code = 'T101 00I'
        op_code = '101I'
        date = '2020-01-01'
        op_program = OPProgram.objects.create(valid_from=date)
        OPDictionary.objects.create(auth_route_code=auth_code, op_route_code=op_code, op_program=op_program)
        query = get_op_route(auth_code, date)
        self.assertEqual(op_code, query)
        op_program.delete()

    def test_get_op_route_wrong_code(self):
        auth_code = 'T101 00I'
        op_code = '101I'
        date = '2020-01-01'
        op_program = OPProgram.objects.create(valid_from=date)
        OPDictionary.objects.create(auth_route_code=auth_code, op_route_code=op_code, op_program=op_program)
        self.assertIsNone(get_op_route('T0000', '2020-01-01'))

    def test__list_parser(self):
        test_list = [[1, 2], [3, 4]]
        expected_list = [{'value': 1, 'item': 2}, {'value': 3, 'item': 4}]
        self.assertEqual(expected_list, _list_parser(test_list))

    def test__dict_parser(self):
        test_list = [[1, 2], [3, 4]]
        expected_dict = {1: 2, 3: 4}
        self.assertEqual(expected_dict, _dict_parser(test_list))

    def test_get_day_type_list_for_select_input(self):
        expected_list = [{'value': 0, 'item': 'Laboral'}, {'value': 1, 'item': 'Sábado'},
                         {'value': 2, 'item': 'Domingo'}]
        self.assertEqual(expected_list, get_day_type_list_for_select_input())

        expected_dict = {0: 'Laboral', 1: 'Sábado', 2: 'Domingo'}
        self.assertEqual(expected_dict, get_day_type_list_for_select_input(to_dict=True))

    def test_get_operator_list_for_select_input(self):
        expected_list = [{'value': 1, 'item': 'Alsacia'}, {'value': 2, 'item': 'Su Bus'},
                         {'value': 3, 'item': 'Buses Vule'},
                         {'value': 4, 'item': 'Express'}, {'value': 5, 'item': 'Buses Metropolitana'},
                         {'value': 6, 'item': 'Red Bus Urbano'}, {'value': 7, 'item': 'STP Santiago'},
                         {'value': 8, 'item': 'Metro'},
                         {'value': 9, 'item': 'Metrotren'}]
        self.assertEqual(expected_list, get_operator_list_for_select_input())

        expected_dict = {1: 'Alsacia', 2: 'Su Bus', 3: 'Buses Vule', 4: 'Express', 5: 'Buses Metropolitana',
                         6: 'Red Bus Urbano',
                         7: 'STP Santiago', 8: 'Metro', 9: 'Metrotren'}

        self.assertEqual(expected_dict, get_operator_list_for_select_input(to_dict=True))

        expected_filter_list = [{'value': 1, 'item': 'Alsacia'}, {'value': 2, 'item': 'Su Bus'},
                                {'value': 3, 'item': 'Buses Vule'}]
        self.assertEqual(expected_filter_list, get_operator_list_for_select_input(filter=[1, 2, 3]))

    def test_get_timeperiod_list_for_select_input(self):
        expected_list_period_1 = [{'value': 1, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
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
                                  {'value': 29, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'},
                                  {'value': 30, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
                                  {'value': 31, 'item': 'Nocturno (01:00:00-05:29:59)'},
                                  {'value': 32, 'item': 'Transición nocturno (05:30:00-06:29:59)'},
                                  {'value': 33, 'item': 'Punta mañana (06:30:00-07:59:59)'},
                                  {'value': 34, 'item': 'Transición punta mañana (08:00:00-09:29:59)'},
                                  {'value': 35, 'item': 'Fuera de punta mañana (09:30:00-12:29:59)'},
                                  {'value': 36, 'item': 'Punta mediodía (12:30:00-13:59:59)'},
                                  {'value': 37, 'item': 'Fuera de punta tarde (14:00:00-16:29:59)'},
                                  {'value': 38, 'item': 'Punta tarde 1 (16:30:00-18:29:59)'},
                                  {'value': 39, 'item': 'Punta tarde 2 (18:30:00-20:29:59)'},
                                  {'value': 40, 'item': 'Fuera de punta nocturno (20:30:00-22:59:59)'},
                                  {'value': 41, 'item': 'Pre nocturno (23:00:00-23:59:59)'},
                                  {'value': 42, 'item': 'Pre nocturno sábado (00:00:00-00:59:59)'},
                                  {'value': 43, 'item': 'Nocturno sábado (01:00:00-05:29:59)'},
                                  {'value': 44, 'item': 'Transición sábado mañana (05:30:00-06:29:59)'},
                                  {'value': 45, 'item': 'Punta mañana sábado (06:30:00-10:59:59)'},
                                  {'value': 46, 'item': 'Mañana sábado (11:00:00-13:29:59)'},
                                  {'value': 47, 'item': 'Punta mediodia sábado (13:30:00-17:29:59)'},
                                  {'value': 48, 'item': 'Tarde sábado (17:30:00-20:29:59)'},
                                  {'value': 49, 'item': 'Transición sábado nocturno (20:30:00-22:59:59)'},
                                  {'value': 50, 'item': 'Pre nocturno sábado (23:00:00-23:59:59)'},
                                  {'value': 51, 'item': 'Pre nocturno domingo (00:00:00-00:59:59)'},
                                  {'value': 52, 'item': 'Nocturno domingo (01:00:00-05:29:59)'},
                                  {'value': 53, 'item': 'Transición domingo mañana (05:30:00-09:29:59)'},
                                  {'value': 54, 'item': 'Mañana domingo (09:30:00-13:29:59)'},
                                  {'value': 55, 'item': 'Mediodia domingo (13:30:00-17:29:59)'},
                                  {'value': 56, 'item': 'Tarde domingo (17:30:00-20:59:59)'},
                                  {'value': 57, 'item': 'Transición domingo nocturno (21:00:00-22:59:59)'},
                                  {'value': 58, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'},
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
                                  {'value': 29, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}]

        self.assertListEqual(expected_list_period_1, get_timeperiod_list_for_select_input())

        expected_dict_period_1 = {1: 'Pre nocturno (00:00:00-00:59:59)', 2: 'Nocturno (01:00:00-05:29:59)',
                                  3: 'Transición nocturno (05:30:00-06:29:59)', 4: 'Punta mañana (06:30:00-08:29:59)',
                                  5: 'Transición punta mañana (08:30:00-09:29:59)',
                                  6: 'Fuera de punta mañana (09:30:00-12:29:59)',
                                  7: 'Punta mediodia (12:30:00-13:59:59)',
                                  8: 'Fuera de punta tarde (14:00:00-17:29:59)', 9: 'Punta tarde (17:30:00-20:29:59)',
                                  10: 'Transición punta tarde (20:30:00-21:29:59)',
                                  11: 'Fuera de punta nocturno (21:30:00-22:59:59)',
                                  12: 'Pre nocturno (23:00:00-23:59:59)',
                                  13: 'Pre nocturno sábado (00:00:00-00:59:59)',
                                  14: 'Nocturno sábado (01:00:00-05:29:59)',
                                  15: 'Transición sábado mañana (05:30:00-06:29:59)',
                                  16: 'Punta mañana sábado (06:30:00-10:59:59)',
                                  17: 'Mañana sábado (11:00:00-13:29:59)',
                                  18: 'Punta mediodia sábado (13:30:00-17:29:59)',
                                  19: 'Tarde sábado (17:30:00-20:29:59)',
                                  20: 'Transición sábado nocturno (20:30:00-22:59:59)',
                                  21: 'Pre nocturno sábado (23:00:00-23:59:59)',
                                  22: 'Pre nocturno domingo (00:00:00-00:59:59)',
                                  23: 'Nocturno domingo (01:00:00-05:29:59)',
                                  24: 'Transición domingo mañana (05:30:00-09:29:59)',
                                  25: 'Mañana domingo (09:30:00-13:29:59)', 26: 'Mediodia domingo (13:30:00-17:29:59)',
                                  27: 'Tarde domingo (17:30:00-20:59:59)',
                                  28: 'Transición domingo nocturno (21:00:00-22:59:59)',
                                  29: 'Pre nocturno domingo (23:00:00-23:59:59)',
                                  30: 'Pre nocturno (00:00:00-00:59:59)', 31: 'Nocturno (01:00:00-05:29:59)',
                                  32: 'Transición nocturno (05:30:00-06:29:59)', 33: 'Punta mañana (06:30:00-07:59:59)',
                                  34: 'Transición punta mañana (08:00:00-09:29:59)',
                                  35: 'Fuera de punta mañana (09:30:00-12:29:59)',
                                  36: 'Punta mediodía (12:30:00-13:59:59)',
                                  37: 'Fuera de punta tarde (14:00:00-16:29:59)',
                                  38: 'Punta tarde 1 (16:30:00-18:29:59)', 39: 'Punta tarde 2 (18:30:00-20:29:59)',
                                  40: 'Fuera de punta nocturno (20:30:00-22:59:59)',
                                  41: 'Pre nocturno (23:00:00-23:59:59)', 42: 'Pre nocturno sábado (00:00:00-00:59:59)',
                                  43: 'Nocturno sábado (01:00:00-05:29:59)',
                                  44: 'Transición sábado mañana (05:30:00-06:29:59)',
                                  45: 'Punta mañana sábado (06:30:00-10:59:59)',
                                  46: 'Mañana sábado (11:00:00-13:29:59)',
                                  47: 'Punta mediodia sábado (13:30:00-17:29:59)',
                                  48: 'Tarde sábado (17:30:00-20:29:59)',
                                  49: 'Transición sábado nocturno (20:30:00-22:59:59)',
                                  50: 'Pre nocturno sábado (23:00:00-23:59:59)',
                                  51: 'Pre nocturno domingo (00:00:00-00:59:59)',
                                  52: 'Nocturno domingo (01:00:00-05:29:59)',
                                  53: 'Transición domingo mañana (05:30:00-09:29:59)',
                                  54: 'Mañana domingo (09:30:00-13:29:59)', 55: 'Mediodia domingo (13:30:00-17:29:59)',
                                  56: 'Tarde domingo (17:30:00-20:59:59)',
                                  57: 'Transición domingo nocturno (21:00:00-22:59:59)',
                                  58: 'Pre nocturno domingo (23:00:00-23:59:59)'}

        self.assertEqual(expected_dict_period_1, get_timeperiod_list_for_select_input(to_dict=True))

        expected_list_period_2 = [{'value': 30, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
                                  {'value': 31, 'item': 'Nocturno (01:00:00-05:29:59)'},
                                  {'value': 32, 'item': 'Transición nocturno (05:30:00-06:29:59)'},
                                  {'value': 33, 'item': 'Punta mañana (06:30:00-07:59:59)'},
                                  {'value': 34, 'item': 'Transición punta mañana (08:00:00-09:29:59)'},
                                  {'value': 35, 'item': 'Fuera de punta mañana (09:30:00-12:29:59)'},
                                  {'value': 36, 'item': 'Punta mediodía (12:30:00-13:59:59)'},
                                  {'value': 37, 'item': 'Fuera de punta tarde (14:00:00-16:29:59)'},
                                  {'value': 38, 'item': 'Punta tarde 1 (16:30:00-18:29:59)'},
                                  {'value': 39, 'item': 'Punta tarde 2 (18:30:00-20:29:59)'},
                                  {'value': 40, 'item': 'Fuera de punta nocturno (20:30:00-22:59:59)'},
                                  {'value': 41, 'item': 'Pre nocturno (23:00:00-23:59:59)'},
                                  {'value': 42, 'item': 'Pre nocturno sábado (00:00:00-00:59:59)'},
                                  {'value': 43, 'item': 'Nocturno sábado (01:00:00-05:29:59)'},
                                  {'value': 44, 'item': 'Transición sábado mañana (05:30:00-06:29:59)'},
                                  {'value': 45, 'item': 'Punta mañana sábado (06:30:00-10:59:59)'},
                                  {'value': 46, 'item': 'Mañana sábado (11:00:00-13:29:59)'},
                                  {'value': 47, 'item': 'Punta mediodia sábado (13:30:00-17:29:59)'},
                                  {'value': 48, 'item': 'Tarde sábado (17:30:00-20:29:59)'},
                                  {'value': 49, 'item': 'Transición sábado nocturno (20:30:00-22:59:59)'},
                                  {'value': 50, 'item': 'Pre nocturno sábado (23:00:00-23:59:59)'},
                                  {'value': 51, 'item': 'Pre nocturno domingo (00:00:00-00:59:59)'},
                                  {'value': 52, 'item': 'Nocturno domingo (01:00:00-05:29:59)'},
                                  {'value': 53, 'item': 'Transición domingo mañana (05:30:00-09:29:59)'},
                                  {'value': 54, 'item': 'Mañana domingo (09:30:00-13:29:59)'},
                                  {'value': 55, 'item': 'Mediodia domingo (13:30:00-17:29:59)'},
                                  {'value': 56, 'item': 'Tarde domingo (17:30:00-20:59:59)'},
                                  {'value': 57, 'item': 'Transición domingo nocturno (21:00:00-22:59:59)'},
                                  {'value': 58, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}]

        self.assertEqual(expected_list_period_2, get_timeperiod_list_for_select_input(filter_id=2))

        expected_dict_period_2 = {30: 'Pre nocturno (00:00:00-00:59:59)', 31: 'Nocturno (01:00:00-05:29:59)',
                                  32: 'Transición nocturno (05:30:00-06:29:59)', 33: 'Punta mañana (06:30:00-07:59:59)',
                                  34: 'Transición punta mañana (08:00:00-09:29:59)',
                                  35: 'Fuera de punta mañana (09:30:00-12:29:59)',
                                  36: 'Punta mediodía (12:30:00-13:59:59)',
                                  37: 'Fuera de punta tarde (14:00:00-16:29:59)',
                                  38: 'Punta tarde 1 (16:30:00-18:29:59)', 39: 'Punta tarde 2 (18:30:00-20:29:59)',
                                  40: 'Fuera de punta nocturno (20:30:00-22:59:59)',
                                  41: 'Pre nocturno (23:00:00-23:59:59)', 42: 'Pre nocturno sábado (00:00:00-00:59:59)',
                                  43: 'Nocturno sábado (01:00:00-05:29:59)',
                                  44: 'Transición sábado mañana (05:30:00-06:29:59)',
                                  45: 'Punta mañana sábado (06:30:00-10:59:59)',
                                  46: 'Mañana sábado (11:00:00-13:29:59)',
                                  47: 'Punta mediodia sábado (13:30:00-17:29:59)',
                                  48: 'Tarde sábado (17:30:00-20:29:59)',
                                  49: 'Transición sábado nocturno (20:30:00-22:59:59)',
                                  50: 'Pre nocturno sábado (23:00:00-23:59:59)',
                                  51: 'Pre nocturno domingo (00:00:00-00:59:59)',
                                  52: 'Nocturno domingo (01:00:00-05:29:59)',
                                  53: 'Transición domingo mañana (05:30:00-09:29:59)',
                                  54: 'Mañana domingo (09:30:00-13:29:59)', 55: 'Mediodia domingo (13:30:00-17:29:59)',
                                  56: 'Tarde domingo (17:30:00-20:59:59)',
                                  57: 'Transición domingo nocturno (21:00:00-22:59:59)',
                                  58: 'Pre nocturno domingo (23:00:00-23:59:59)'}

        self.assertEqual(expected_dict_period_2, get_timeperiod_list_for_select_input(to_dict=True, filter_id=2))

    def test_get_halfhour_list_for_select_input(self):
        expected_list = [{'value': 0, 'item': '00:00:00-00:29:59'}, {'value': 1, 'item': '00:30:00-00:59:59'},
                         {'value': 2, 'item': '01:00:00-01:29:59'}, {'value': 3, 'item': '01:30:00-01:59:59'},
                         {'value': 4, 'item': '02:00:00-02:29:59'}, {'value': 5, 'item': '02:30:00-02:59:59'},
                         {'value': 6, 'item': '03:00:00-03:29:59'}, {'value': 7, 'item': '03:30:00-03:59:59'},
                         {'value': 8, 'item': '04:00:00-04:29:59'}, {'value': 9, 'item': '04:30:00-04:59:59'},
                         {'value': 10, 'item': '05:00:00-05:29:59'}, {'value': 11, 'item': '05:30:00-05:59:59'},
                         {'value': 12, 'item': '06:00:00-06:29:59'}, {'value': 13, 'item': '06:30:00-06:59:59'},
                         {'value': 14, 'item': '07:00:00-07:29:59'}, {'value': 15, 'item': '07:30:00-07:59:59'},
                         {'value': 16, 'item': '08:00:00-08:29:59'}, {'value': 17, 'item': '08:30:00-08:59:59'},
                         {'value': 18, 'item': '09:00:00-09:29:59'}, {'value': 19, 'item': '09:30:00-09:59:59'},
                         {'value': 20, 'item': '10:00:00-10:29:59'}, {'value': 21, 'item': '10:30:00-10:59:59'},
                         {'value': 22, 'item': '11:00:00-11:29:59'}, {'value': 23, 'item': '11:30:00-11:59:59'},
                         {'value': 24, 'item': '12:00:00-12:29:59'}, {'value': 25, 'item': '12:30:00-12:59:59'},
                         {'value': 26, 'item': '13:00:00-13:29:59'}, {'value': 27, 'item': '13:30:00-13:59:59'},
                         {'value': 28, 'item': '14:00:00-14:29:59'}, {'value': 29, 'item': '14:30:00-14:59:59'},
                         {'value': 30, 'item': '15:00:00-15:29:59'}, {'value': 31, 'item': '15:30:00-15:59:59'},
                         {'value': 32, 'item': '16:00:00-16:29:59'}, {'value': 33, 'item': '16:30:00-16:59:59'},
                         {'value': 34, 'item': '17:00:00-17:29:59'}, {'value': 35, 'item': '17:30:00-17:59:59'},
                         {'value': 36, 'item': '18:00:00-18:29:59'}, {'value': 37, 'item': '18:30:00-18:59:59'},
                         {'value': 38, 'item': '19:00:00-19:29:59'}, {'value': 39, 'item': '19:30:00-19:59:59'},
                         {'value': 40, 'item': '20:00:00-20:29:59'}, {'value': 41, 'item': '20:30:00-20:59:59'},
                         {'value': 42, 'item': '21:00:00-21:29:59'}, {'value': 43, 'item': '21:30:00-21:59:59'},
                         {'value': 44, 'item': '22:00:00-22:29:59'}, {'value': 45, 'item': '22:30:00-22:59:59'},
                         {'value': 46, 'item': '23:00:00-23:29:59'}, {'value': 47, 'item': '23:30:00-23:59:59'}]
        self.assertEqual(expected_list, get_halfhour_list_for_select_input())
        expected_dict = {0: '00:00:00-00:29:59', 1: '00:30:00-00:59:59', 2: '01:00:00-01:29:59', 3: '01:30:00-01:59:59',
                         4: '02:00:00-02:29:59', 5: '02:30:00-02:59:59', 6: '03:00:00-03:29:59', 7: '03:30:00-03:59:59',
                         8: '04:00:00-04:29:59', 9: '04:30:00-04:59:59', 10: '05:00:00-05:29:59',
                         11: '05:30:00-05:59:59', 12: '06:00:00-06:29:59', 13: '06:30:00-06:59:59',
                         14: '07:00:00-07:29:59', 15: '07:30:00-07:59:59', 16: '08:00:00-08:29:59',
                         17: '08:30:00-08:59:59', 18: '09:00:00-09:29:59', 19: '09:30:00-09:59:59',
                         20: '10:00:00-10:29:59', 21: '10:30:00-10:59:59', 22: '11:00:00-11:29:59',
                         23: '11:30:00-11:59:59', 24: '12:00:00-12:29:59', 25: '12:30:00-12:59:59',
                         26: '13:00:00-13:29:59', 27: '13:30:00-13:59:59', 28: '14:00:00-14:29:59',
                         29: '14:30:00-14:59:59', 30: '15:00:00-15:29:59', 31: '15:30:00-15:59:59',
                         32: '16:00:00-16:29:59', 33: '16:30:00-16:59:59', 34: '17:00:00-17:29:59',
                         35: '17:30:00-17:59:59', 36: '18:00:00-18:29:59', 37: '18:30:00-18:59:59',
                         38: '19:00:00-19:29:59', 39: '19:30:00-19:59:59', 40: '20:00:00-20:29:59',
                         41: '20:30:00-20:59:59', 42: '21:00:00-21:29:59', 43: '21:30:00-21:59:59',
                         44: '22:00:00-22:29:59', 45: '22:30:00-22:59:59', 46: '23:00:00-23:29:59',
                         47: '23:30:00-23:59:59'}
        self.assertEqual(expected_dict, get_halfhour_list_for_select_input(to_dict=True))

    def test_get_commune_list_for_select_input(self):
        expected_list = [{'value': 0, 'item': 'LAMPA'}, {'value': 1, 'item': 'COLINA'},
                         {'value': 2, 'item': 'LO BARNECHEA'}, {'value': 3, 'item': 'LAS CONDES'},
                         {'value': 4, 'item': 'PENALOLEN'}, {'value': 5, 'item': 'LA FLORIDA'},
                         {'value': 6, 'item': 'PUENTE ALTO'}, {'value': 7, 'item': 'SAN JOSE DE MAIPO'},
                         {'value': 8, 'item': 'SAN BERNARDO'}, {'value': 9, 'item': 'ISLA DE MAIPO'},
                         {'value': 10, 'item': 'TALAGANTE'}, {'value': 11, 'item': 'CALERA DE TANGO'},
                         {'value': 12, 'item': 'PENAFLOR'}, {'value': 13, 'item': 'PADRE HURTADO'},
                         {'value': 14, 'item': 'MAIPU'}, {'value': 15, 'item': 'PUDAHUEL'},
                         {'value': 16, 'item': 'ESTACION CENTRAL'}, {'value': 17, 'item': 'LO PRADO'},
                         {'value': 18, 'item': 'CERRO NAVIA'}, {'value': 19, 'item': 'RENCA'},
                         {'value': 20, 'item': 'QUILICURA'}, {'value': 21, 'item': 'HUECHURABA'},
                         {'value': 22, 'item': 'VITACURA'}, {'value': 23, 'item': 'PROVIDENCIA'},
                         {'value': 24, 'item': 'LA REINA'}, {'value': 25, 'item': 'NUNOA'},
                         {'value': 26, 'item': 'MACUL'}, {'value': 27, 'item': 'SAN JOAQUIN'},
                         {'value': 28, 'item': 'LA GRANJA'}, {'value': 29, 'item': 'LA PINTANA'},
                         {'value': 30, 'item': 'EL BOSQUE'}, {'value': 31, 'item': 'LO ESPEJO'},
                         {'value': 32, 'item': 'CERRILLOS'}, {'value': 33, 'item': 'PEDRO AGUIRRE CERDA'},
                         {'value': 34, 'item': 'SANTIAGO'}, {'value': 35, 'item': 'QUINTA NORMAL'},
                         {'value': 36, 'item': 'INDEPENDENCIA'}, {'value': 37, 'item': 'CONCHALI'},
                         {'value': 38, 'item': 'RECOLETA'}, {'value': 39, 'item': 'SAN MIGUEL'},
                         {'value': 40, 'item': 'SAN RAMON'}, {'value': 41, 'item': 'LA CISTERNA'}]
        self.assertEqual(expected_list, get_commune_list_for_select_input())
        expected_dict = {0: 'LAMPA', 1: 'COLINA', 2: 'LO BARNECHEA', 3: 'LAS CONDES', 4: 'PENALOLEN', 5: 'LA FLORIDA',
                         6: 'PUENTE ALTO', 7: 'SAN JOSE DE MAIPO', 8: 'SAN BERNARDO', 9: 'ISLA DE MAIPO',
                         10: 'TALAGANTE', 11: 'CALERA DE TANGO', 12: 'PENAFLOR', 13: 'PADRE HURTADO', 14: 'MAIPU',
                         15: 'PUDAHUEL', 16: 'ESTACION CENTRAL', 17: 'LO PRADO', 18: 'CERRO NAVIA', 19: 'RENCA',
                         20: 'QUILICURA', 21: 'HUECHURABA', 22: 'VITACURA', 23: 'PROVIDENCIA', 24: 'LA REINA',
                         25: 'NUNOA', 26: 'MACUL', 27: 'SAN JOAQUIN', 28: 'LA GRANJA', 29: 'LA PINTANA',
                         30: 'EL BOSQUE', 31: 'LO ESPEJO', 32: 'CERRILLOS', 33: 'PEDRO AGUIRRE CERDA', 34: 'SANTIAGO',
                         35: 'QUINTA NORMAL', 36: 'INDEPENDENCIA', 37: 'CONCHALI', 38: 'RECOLETA', 39: 'SAN MIGUEL',
                         40: 'SAN RAMON', 41: 'LA CISTERNA'}
        self.assertDictEqual(expected_dict, get_commune_list_for_select_input(to_dict=True))

    def test_get_transport_mode_list_for_select_input(self):
        expected_list = [{'value': 1, 'item': 'Bus'}, {'value': 2, 'item': 'Metro'},
                         {'value': 3, 'item': 'Bus + Metro'}, {'value': 4, 'item': 'MetroTren'},
                         {'value': 5, 'item': 'Bus + Metrotren'}, {'value': 6, 'item': 'Metro + Metrotren'},
                         {'value': 7, 'item': 'Bus + Metro + Metrotren'}]
        self.assertEqual(expected_list, get_transport_mode_list_for_select_input())
        expected_dict = {1: 'Bus', 2: 'Metro', 3: 'Bus + Metro', 4: 'MetroTren', 5: 'Bus + Metrotren',
                         6: 'Metro + Metrotren', 7: 'Bus + Metro + Metrotren'}
        self.assertEqual(expected_dict, get_transport_mode_list_for_select_input(to_dict=True))

    def test_get_calendar_info(self):
        test_day = DayDescription(color='#000000', description='Día Soleado')
        test_day.save()
        test_date = CalendarInfo(date=datetime(2020, 4, 20), day_description_id=test_day.id)
        test_date.save()
        expected_calendar_info = [
            {'date': datetime(2020, 4, 20).date(), 'color': '#000000', 'description': 'Día Soleado'}]
        self.assertEqual(expected_calendar_info, get_calendar_info())

    def test_all_faqs(self):
        expected_answer = {'route': [self.test_faq]}
        self.assertEqual(expected_answer, get_all_faqs())

    def test_search_faq(self):
        expected_answer = {'route': [self.test_faq]}
        self.assertEqual(expected_answer, search_faq('pregunta'))

    def test_get_valid_time_period_date(self):
        valid_dates_list_first = ['2017-01-01', '2018-01-01']
        valid_dates_list_second = ['2020-06-27', '2020-07-01']
        invalid_dates_list = ['2017-01-01', '2020-07-01']
        answer_first = True, 1
        answer_second = True, 2
        answer_invalid = False, ''
        self.assertEqual(answer_first, get_valid_time_period_date(valid_dates_list_first))
        self.assertEqual(answer_second, get_valid_time_period_date(valid_dates_list_second))
        self.assertEqual(answer_invalid, get_valid_time_period_date(invalid_dates_list))

    @mock.patch('localinfo.helper.ESOPDataHelper')
    def test_synchronize_op_program_empty_case(self, es_opdata_helper):
        es_opdata_helper.return_value.get_available_days.return_value = []
        expected_dict = {'es_available_days': set(), 'db_available_days': set(), 'created': set(), 'deleted': set()}
        self.assertEqual(expected_dict, synchronize_op_program())

    @mock.patch('localinfo.helper.ESOPDataHelper')
    def test_synchronize_op_program_only_es_case(self, es_opdata_helper):
        es_available_days = {'2019-01-01', '2020-01-01'}
        es_opdata_helper.return_value.get_available_days.return_value = list(es_available_days)
        expected_dict = {'es_available_days': es_available_days,
                         'db_available_days': set(),
                         'created': es_available_days,
                         'deleted': set()
                         }
        self.assertEqual(expected_dict, synchronize_op_program())
        for day in expected_dict['created']:
            OPProgram.objects.get(valid_from=day)

    @mock.patch('localinfo.helper.ESOPDataHelper')
    def test_synchronize_op_program_only_db_case(self, es_opdata_helper):
        es_opdata_helper.return_value.get_available_days.return_value = []
        db_days = {'2020-01-01', '2019-01-01'}
        for day in db_days:
            OPProgram.objects.create(valid_from=day)
        expected_dict = {'es_available_days': set(),
                         'db_available_days': db_days,
                         'created': set(),
                         'deleted': db_days
                         }
        self.assertEqual(expected_dict, synchronize_op_program())
        self.assertEqual(len(OPProgram.objects.all()), 0)

    @mock.patch('localinfo.helper.ESOPDataHelper')
    def test_synchronize_op_program_mix_case(self, es_opdata_helper):
        es_available_days = {'2019-01-01', '2020-01-01', '2019-07-09'}
        db_days = {'2020-01-01', '2019-01-01', '2021-01-01'}
        es_opdata_helper.return_value.get_available_days.return_value = list(es_available_days)

        for day in db_days:
            OPProgram.objects.create(valid_from=day)

        expected_dict = {'es_available_days': es_available_days,
                         'db_available_days': db_days,
                         'created': es_available_days - db_days,
                         'deleted': db_days - es_available_days
                         }
        self.assertEqual(expected_dict, synchronize_op_program())
        for day in expected_dict['created']:
            OPProgram.objects.get(valid_from=day)

    def test_upload_csv_op_dictionary(self):
        file_names = ['diccionario_op_base.csv', 'diccionario_op_base.csv.gz', 'diccionario_op_base.zip']

        def create_op_program_and_upload(name):
            op_program = OPProgram.objects.create(valid_from='2020-11-28')
            file = os.path.join(self.path, name)
            opened_file = open(file, 'rb')
            django_file = InMemoryUploadedFile(opened_file, None, name, 'text',
                                               opened_file.__sizeof__(), None)
            expected_res = {"created": 7}
            self.assertEqual(expected_res, upload_csv_op_dictionary(django_file, op_program.id))
            opened_file.close()
            op_program.delete()

        for file_name in file_names:
            create_op_program_and_upload(file_name)

    def test_upload_csv_op_dictionary_error(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        file = os.path.join(self.path, 'diccionario_op_base_error.csv')
        opened_file = open(file, 'rb')
        django_file = InMemoryUploadedFile(opened_file, None, 'diccionario_op_base_error.csv', 'text',
                                           opened_file.__sizeof__(), None)

        with self.assertRaises(IndexError):
            upload_csv_op_dictionary(django_file, op_program.id)
        op_program.delete()

    def test_upload_csv_op_dictionary_wrong_op(self):
        file = os.path.join(self.path, 'diccionario_op_base_error.csv')
        opened_file = open(file, 'rb')
        django_file = InMemoryUploadedFile(opened_file, None, 'diccionario_op_base_error.csv', 'text',
                                           opened_file.__sizeof__(), None)

        with self.assertRaises(OPProgram.DoesNotExist):
            upload_csv_op_dictionary(django_file, -1)

    def test_get_opprogram_list_for_select_input(self):
        op_program = OPProgram.objects.create(valid_from='2020-01-01')
        expected_list = [{'value': op_program.id, 'item': '2020-01-01'}]
        self.assertEqual(expected_list, get_opprogram_list_for_select_input())

    def test_get_get_periods_dict(self):
        expected_answer = {1: [{'value': 1, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
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
                               {'value': 29, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}],
                           2: [{'value': 30, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
                               {'value': 31, 'item': 'Nocturno (01:00:00-05:29:59)'},
                               {'value': 32, 'item': 'Transición nocturno (05:30:00-06:29:59)'},
                               {'value': 33, 'item': 'Punta mañana (06:30:00-07:59:59)'},
                               {'value': 34, 'item': 'Transición punta mañana (08:00:00-09:29:59)'},
                               {'value': 35, 'item': 'Fuera de punta mañana (09:30:00-12:29:59)'},
                               {'value': 36, 'item': 'Punta mediodía (12:30:00-13:59:59)'},
                               {'value': 37, 'item': 'Fuera de punta tarde (14:00:00-16:29:59)'},
                               {'value': 38, 'item': 'Punta tarde 1 (16:30:00-18:29:59)'},
                               {'value': 39, 'item': 'Punta tarde 2 (18:30:00-20:29:59)'},
                               {'value': 40, 'item': 'Fuera de punta nocturno (20:30:00-22:59:59)'},
                               {'value': 41, 'item': 'Pre nocturno (23:00:00-23:59:59)'},
                               {'value': 42, 'item': 'Pre nocturno sábado (00:00:00-00:59:59)'},
                               {'value': 43, 'item': 'Nocturno sábado (01:00:00-05:29:59)'},
                               {'value': 44, 'item': 'Transición sábado mañana (05:30:00-06:29:59)'},
                               {'value': 45, 'item': 'Punta mañana sábado (06:30:00-10:59:59)'},
                               {'value': 46, 'item': 'Mañana sábado (11:00:00-13:29:59)'},
                               {'value': 47, 'item': 'Punta mediodia sábado (13:30:00-17:29:59)'},
                               {'value': 48, 'item': 'Tarde sábado (17:30:00-20:29:59)'},
                               {'value': 49, 'item': 'Transición sábado nocturno (20:30:00-22:59:59)'},
                               {'value': 50, 'item': 'Pre nocturno sábado (23:00:00-23:59:59)'},
                               {'value': 51, 'item': 'Pre nocturno domingo (00:00:00-00:59:59)'},
                               {'value': 52, 'item': 'Nocturno domingo (01:00:00-05:29:59)'},
                               {'value': 53, 'item': 'Transición domingo mañana (05:30:00-09:29:59)'},
                               {'value': 54, 'item': 'Mañana domingo (09:30:00-13:29:59)'},
                               {'value': 55, 'item': 'Mediodia domingo (13:30:00-17:29:59)'},
                               {'value': 56, 'item': 'Tarde domingo (17:30:00-20:59:59)'},
                               {'value': 57, 'item': 'Transición domingo nocturno (21:00:00-22:59:59)'},
                               {'value': 58, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}],
                           3: [{'value': 1, 'item': 'Pre nocturno (00:00:00-00:59:59)'},
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
                               {'value': 29, 'item': 'Pre nocturno domingo (23:00:00-23:59:59)'}],
                           }

        self.assertDictEqual(expected_answer, get_periods_dict())

    def test_check_period_list_id(self):
        correct_period_list = [33, 34, 35, 36, 37, 38, 39]
        correct_period_id = [2]
        self.assertEqual(correct_period_id, check_period_list_id(correct_period_list))
        multiple_period_list = [3, 4, 5, 6, 7, 8, 9]
        multiple_period_id = [1, 3]
        self.assertEqual(multiple_period_id, check_period_list_id(multiple_period_list))
        null_period_list = [420]
        self.assertEqual([], check_period_list_id(null_period_list))
