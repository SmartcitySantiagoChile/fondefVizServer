# -*- coding: utf-8 -*-
import csv
import json
import os

from django.urls import reverse

from localinfo.models import OPDictionary
from testhelper.helper import TestHelper


class LocalInfoViewTest(TestHelper):
    fixtures = ['daytypes', 'operators', 'timeperioddates', 'timeperiods', 'halfhours', 'communes',
                'transportmodes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
        self.data = {
        }

    def test_OPDictionaryCsvUploader_post(self):
        with open(os.path.join(self.path, 'op_data.csv'), 'r') as file:
            response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': file})
            self.assertEqual(200, response.status_code)
        with open(os.path.join(self.path, 'op_data_2.csv'), 'r') as file:
            response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': file})
            self.assertEqual(200, response.status_code)
        saved_objects = OPDictionary.objects.all()
        with open(os.path.join(self.path, 'op_data_2.csv'), 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                self.assertTrue(
                    saved_objects.filter(auth_route_code=row[0], user_route_code=row[1], op_route_code=row[2],
                                         route_type=row[3]).exists())
        bad_response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': ''})
        self.assertEqual(400, bad_response.status_code)

    def test_OPDictionaryCsvUploaderError_post(self):
        with open(os.path.join(self.path, 'op_data_error.csv'), 'r') as file:
            response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': file})
            self.assertEqual(400, response.status_code)

    def test_TimePeriod_error(self):
        self.data['dates[]'] = ['2017-01-01', '2020-07-01']
        url = reverse('timePeriod')
        response = self.client.get(url, self.data)
        self.assertEqual(400, response.status_code)

    def test_TimePeriod(self):
        self.data['dates[]'] = ['2017-01-01', '2017-07-01']
        url = reverse('timePeriod')
        response = self.client.get(url, self.data)
        expected_time_period = {'timePeriod': [{'value': 1, 'item': 'Pre nocturno'}, {'value': 2, 'item': 'Nocturno'},
                                               {'value': 3, 'item': 'Transición nocturno'},
                                               {'value': 4, 'item': 'Punta mañana'},
                                               {'value': 5, 'item': 'Transición punta mañana'},
                                               {'value': 6, 'item': 'Fuera de punta mañana'},
                                               {'value': 7, 'item': 'Punta mediodia'},
                                               {'value': 8, 'item': 'Fuera de punta tarde'},
                                               {'value': 9, 'item': 'Punta tarde'},
                                               {'value': 10, 'item': 'Transición punta tarde'},
                                               {'value': 11, 'item': 'Fuera de punta nocturno'},
                                               {'value': 12, 'item': 'Pre nocturno'},
                                               {'value': 13, 'item': 'Pre nocturno sábado'},
                                               {'value': 14, 'item': 'Nocturno sábado'},
                                               {'value': 15, 'item': 'Transición sábado mañana'},
                                               {'value': 16, 'item': 'Punta mañana sábado'},
                                               {'value': 17, 'item': 'Mañana sábado'},
                                               {'value': 18, 'item': 'Punta mediodia sábado'},
                                               {'value': 19, 'item': 'Tarde sábado'},
                                               {'value': 20, 'item': 'Transición sábado nocturno'},
                                               {'value': 21, 'item': 'Pre nocturno sábado'},
                                               {'value': 22, 'item': 'Pre nocturno domingo'},
                                               {'value': 23, 'item': 'Nocturno domingo'},
                                               {'value': 24, 'item': 'Transición domingo mañana'},
                                               {'value': 25, 'item': 'Mañana domingo'},
                                               {'value': 26, 'item': 'Mediodia domingo'},
                                               {'value': 27, 'item': 'Tarde domingo'},
                                               {'value': 28, 'item': 'Transición domingo nocturno'},
                                               {'value': 29, 'item': 'Pre nocturno domingo'}]}
        print(json.loads(response.content))
        self.assertEqual(200, response.status_code)
