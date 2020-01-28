# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from esapi.errors import ESQueryDateParametersDoesNotExist, FondefVizError
from esapi.helper.bip import ESBipHelper
from esapi.utils import get_dates_from_request
from localinfo.helper import get_calendar_info, PermissionBuilder


class AvailableDays(View):

    def get(self, request):
        es_helper = ESBipHelper()
        available_days = es_helper.get_available_days()
        calendar_info = get_calendar_info()
        response = {
            'availableDays': available_days,
            'info': calendar_info
        }

        return JsonResponse(response)


class BipTransactionByOperatorData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BipTransactionByOperatorData, self).dispatch(request, *args, **kwargs)

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value < 0) else value

    def transform_es_answer(self, es_query):
        result = {}
        return result

    def process_request(self, request, params, export_data=False):
        response = {}
        dates = get_dates_from_request(request, export_data)
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        try:
            if len(dates) == 0:
                raise ESQueryDateParametersDoesNotExist
            es_helper = ESBipHelper()
            es_query = es_helper.get_bip_by_operator_data(dates, valid_operator_list)
            print(es_query)

        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
