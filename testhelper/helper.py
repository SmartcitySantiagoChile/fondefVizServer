# -*- encoding: utf-8 -*-
import json

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse

from localinfo.helper import PermissionBuilder


class TestHelper(TestCase):
    fixtures = ['operators']

    def create_logged_client(self, username='username', password='password', email='a@b.cl'):
        User.objects.create_superuser(username, email, password)
        logged_client = Client()
        response = logged_client.login(username=username, password=password)
        self.assertTrue(response)
        return logged_client

    def create_logged_client_with_global_permission(self, username='username', password='password', email='a@b.cl'):
        PermissionBuilder().create_permission_based_on_operators()
        user = User.objects.create_superuser(username, email, password)
        group_obj = Group.objects.get(name='Transantiago')
        user.groups.add(group_obj)
        logged_client = Client()
        response = logged_client.login(username=username, password=password)
        self.assertTrue(response)
        return logged_client

    def check_http_response(self, client, url, status_code, data=None):
        response = client.get(reverse(url), data)
        self.assertEqual(status_code, response.status_code)
        return response

    def check_json_response(self, client, url, status_code, data=None):
        response = client.get(reverse(url), data)
        self.assertEqual(status_code, response.status_code)
        return json.loads(response.content)


