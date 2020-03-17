# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper


class GetRouteInfo(View):
    """ get shape and stop related with route """

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
            es_stop_helper = ESStopByRouteHelper()

            response["points"] = es_shape_helper.get_route_shape(route, [[operation_program_date]])[
                'points']
            response["stops"] = es_stop_helper.get_stop_list(route, [[operation_program_date]])[
                'stops']
        except FondefVizError as e:
            response['status'] = e.get_status_response()
        return JsonResponse(response)


class MapHTML(View):
    """ load html map to show route polyline """

    def get(self, request):
        template = "shape/map.html"
        context = {}

        return render(request, template, context)
