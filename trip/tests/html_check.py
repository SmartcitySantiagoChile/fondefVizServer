# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class TestHelper(TestCase):

    def create_logged_client(self, username='username', password='password', email='a@b.cl'):
        """ get test logged test client  """

        # create user on django contrib user model
        User.objects.create_superuser(username=username, email=email, password=password)

        # log in process
        client = Client()
        response = client.login(username=username, password=password)
        self.assertTrue(response)

        return client

    def check_html(self, url):
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        print((response.content))
        self.html


class HTMLAccess(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client()

    def test_site_fromtomap(self):
        url = reverse('trip:from-to')
        self.check_html(url)

    def test_site_largetrips(self):
        url = reverse('trip:large-trips')
        self.check_html(url)

    def test_site_map(self):
        url = reverse('trip:map')
        self.check_html(url)

    def test_site_strategies(self):
        url = reverse('trip:strategies')
        self.check_html(url)

    def test_site_resume(self):
        url = reverse('trip:graphs')
        self.check_html(url)
