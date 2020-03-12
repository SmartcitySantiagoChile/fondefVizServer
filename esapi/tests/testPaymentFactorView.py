# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django.urls import reverse

from testhelper.helper import TestHelper


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availablePaymentfactorDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.paymentfactor.ESPaymentFactorHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        expected = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, expected)
