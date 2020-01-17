# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.errors import FondefVizError, ESQueryDateParametersDoesNotExist
from esapi.utils import check_operation_program, get_dates_from_request
from esapi.messages import ExporterDataHasBeenEnqueuedMessage

from localinfo.helper import PermissionBuilder

from datamanager.helper import ExporterManager

import rqworkers.dataDownloader.csvhelper.helper as csv_helper


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

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ODMatrixData, self).dispatch(request, *args, **kwargs)

    def process_request(self, request, params, export_data=False):

        dates = get_dates_from_request(request, export_data)

        day_type = params.getlist('dayType[]')
        period = params.getlist('period[]')
        auth_route_code = params.get('authRoute')

        response = {
            'data': {}
        }

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        try:
            if len(dates) == 0:
                raise ESQueryDateParametersDoesNotExist
            for date_range in dates:
                check_operation_program(date_range[0], date_range[len(date_range) - 1])
            es_od_helper = ESODByRouteHelper()
            es_stop_helper = ESStopByRouteHelper()

            if export_data:
                es_query = es_od_helper.get_base_query_for_od(auth_route_code, period, day_type, dates,
                                                              valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.OD_BY_ROUTE_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                matrix, max_value = es_od_helper.get_od_data(auth_route_code, period, day_type, dates,
                                                             valid_operator_list)
                stop_list = es_stop_helper.get_stop_list(auth_route_code, dates)['stops']

                response["data"] = {
                    "matrix": matrix,
                    "maximum": max_value,
                    "stopList": stop_list
                }
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
