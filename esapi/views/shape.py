# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views import View

from esapi.helper.shape import ESShapeHelper
from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist


class GetRouteShape(View):
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

            es_shape_helper = ESShapeHelper()

            response["points"] = es_shape_helper.get_route_shape(route, [operation_program_date])[
                'points']
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)
