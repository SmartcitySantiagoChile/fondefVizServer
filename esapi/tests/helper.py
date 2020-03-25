# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import Client


class TestHelper:
    """ methods that help to create test cases """

    def __init__(self, test_instance):
        self.test_instance = test_instance

    def create_logged_client(self, username='fake_user', password='fake_password', email='a@b.cl'):
        """ get test logged test client  """

        # create user on django contrib user model
        User.objects.create_superuser(username=username, email=email, password=password)

        # log in process
        client = Client()
        response = client.login(username=username, password=password)
        self.test_instance.assertTrue(response)

        return client
