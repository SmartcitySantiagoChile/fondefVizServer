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
        self.assertEqual(200, response.status_code)
