# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views import View

from esapi.helper.stop import ESStopHelper
from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist


class GetRouteStop(View):
    """ get polyline of route """

    def get(self, request):
        route = request.GET.get('route', '')
        operation_program_date = request.GET.get('operationProgramDate', '')

        response = {}
        try:
            if not route:
                raise ESQueryRouteParameterDoesNotExist()
            if not operation_program_date:
                raise ESQueryDateParametersDoesNotExist()

            es_stop_helper = ESStopHelper()

            response["stops"] = es_stop_helper.get_stop_list(route, operation_program_date, operation_program_date)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)
