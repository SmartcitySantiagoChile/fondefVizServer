# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.generic import View

from esapi.errors import FondefVizError
from esapi.helper.bip import ESBipHelper
from localinfo.helper import PermissionBuilder, get_calendar_info


class AvailableDays(View):

    def get(self, request):
        es_helper = ESBipHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.get_available_days(valid_operator_list)
        calendar_info = get_calendar_info()
        response = {
            'availableDays': available_days,
            'info': calendar_info
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):

        response = {}
        try:
            es_helper = ESBipHelper()
            valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
            available_days, op_dict = es_helper.get_available_routes(valid_operator_list)

            response['availableRoutes'] = available_days
            response['operatorDict'] = op_dict
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

