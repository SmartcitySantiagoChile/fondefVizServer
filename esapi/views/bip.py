# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import rqworkers.dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import ESQueryDateParametersDoesNotExist, FondefVizError, ESQueryResultEmpty
from esapi.helper.bip import ESBipHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
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
        """ transform ES answer to something util to web client """
        histogram = []
        response = es_query.execute()
        for hit in response.aggregations.histogram:
            histogram.append(hit.to_dict())
        if len(histogram) == 0:
            raise ESQueryResultEmpty()
        return histogram

    def process_request(self, request, params, export_data=False):
        response = {}
        dates = get_dates_from_request(request, export_data)
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        try:
            if len(dates) == 0:
                raise ESQueryDateParametersDoesNotExist
            es_helper = ESBipHelper()
            es_query, operator_list = es_helper.get_bip_by_operator_data(dates, valid_operator_list)

            if export_data:
                ExporterManager(es_query).export_data(csv_helper.BIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response = self.transform_es_answer(es_query)
                response = {
                    'data': response,
                    'operators': operator_list
                }

        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
