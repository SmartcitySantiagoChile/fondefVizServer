# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse

from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.stop import ESStopHelper
from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty


class AvailableDays(View):

    def get(self, request):
        es_helper = ESODByRouteHelper()
        available_days = es_helper.ask_for_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):
        es_helper = ESODByRouteHelper()
        available_days, op_dict = es_helper.ask_for_available_routes()

        response = {
            'availableRoutes': available_days,
            'operatorDict': op_dict
        }

        return JsonResponse(response)


class ODMatrixData(View):

    def get(self, request):
        """ data data """

        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_type = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        route = request.GET.get('authRoute')

        response = {
            'data': {}
        }

        es_od_helper = ESODByRouteHelper()
        es_stop_helper = ESStopHelper()

        try:
            if not route:
                raise ESQueryRouteParameterDoesNotExist()

            matrix, max_value = es_od_helper.ask_for_od(route, period, day_type, start_date, end_date)
            stop_list = es_stop_helper.get_stop_list(route, start_date,
                                                     fields=['userStopCode', 'stopName', 'authStopCode', 'order'])

            response["data"] = {
                "matrix": matrix,
                "maximum": max_value,
                "stopList": stop_list
            }

            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)
