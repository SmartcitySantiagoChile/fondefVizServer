# -*- coding: utf-8 -*-
import csv
import os

from django.test import TestCase

from localinfo.models import OPDictionary, CustomRoute
from localinfo.tests.helper import TestHelper
from django.urls import reverse


class LocalInfoViewTest(TestCase):

    def setUp(self):
        self.helper = TestHelper(self)
        self.client = self.helper.create_logged_client()
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')

    def test_OPDictionaryCsvUploader_post(self):
        with open(os.path.join(self.path, 'opdictionary.csv'), 'r') as file:
            response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': file})
            saved_objects = OPDictionary.objects.all()
            self.assertEqual(200, response.status_code)
        with open(os.path.join(self.path, 'opdictionary.csv'), 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                self.assertTrue(saved_objects.filter(auth_route_code=row[0], op_route_code=row[1]).exists())
        bad_response = self.client.post(reverse('opdictionarycsvupload'), {'name': 'file.csv', 'csvDictionary': ''})
        self.assertEqual(400, bad_response.status_code)

    def test_CustomRouteCsvUploader_post(self):
        with open(os.path.join(self.path, 'opdictionary.csv'), 'r') as file:
            response = self.client.post(reverse('customroutecsvupload'), {'name': 'file.csv', 'csvDictionary': file})
            saved_objects = CustomRoute.objects.all()
            self.assertEqual(200, response.status_code)
        with open(os.path.join(self.path, 'opdictionary.csv'), 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                self.assertTrue(saved_objects.filter(auth_route_code=row[0], custom_route_code=row[1]).exists())
        bad_response = self.client.post(reverse('customroutecsvupload'), {'name': 'file.csv', 'csvDictionary': ''})
        self.assertEqual(400, bad_response.status_code)
