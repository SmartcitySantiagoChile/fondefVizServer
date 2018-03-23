# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse

from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.stop import ESStopHelper
from esapi.errors import FondefVizError
from esapi.utils import check_operation_program
from esapi.messages import ExporterDataHasBeenEnqueuedMessage

from localinfo.helper import PermissionBuilder

from datamanager.helper import ExporterManager


class AvailableDays(View):

    def get(self, request):
        es_helper = ESODByRouteHelper()
        valid_operator_id_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.get_available_days(valid_operator_id_list)

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):
        es_helper = ESODByRouteHelper()
        valid_operator_id_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days, op_dict = es_helper.get_available_routes(valid_operator_id_list)

        response = {
            'availableRoutes': available_days,
            'operatorDict': op_dict
        }

        return JsonResponse(response)


class ODMatrixData(View):

    def process_request(self, request, params, export_data=False):

        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_type = params.getlist('dayType[]')
        period = params.getlist('period[]')
        auth_route_code = params.get('authRoute')

        response = {
            'data': {}
        }

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        try:
            check_operation_program(start_date, end_date)
            es_od_helper = ESODByRouteHelper()
            es_stop_helper = ESStopHelper()

            if export_data:
                es_query = es_od_helper.get_base_query_for_od(auth_route_code, period, day_type, start_date, end_date,
                                                              valid_operator_list)
                ExporterManager(es_query).export_data()
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                matrix, max_value = es_od_helper.get_od_data(auth_route_code, period, day_type, start_date, end_date,
                                                             valid_operator_list)
                stop_list = es_stop_helper.get_stop_list(auth_route_code, start_date, end_date)['stops']

                response["data"] = {
                    "matrix": matrix,
                    "maximum": max_value,
                    "stopList": stop_list
                }
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        self.process_request(request, request.GET)

    def post(self, request):
        self.process_request(request, request.POST, export_data=True)
