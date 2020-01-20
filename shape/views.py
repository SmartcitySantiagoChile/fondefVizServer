# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.shortcuts import render
from django.http import JsonResponse

from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist

from datetime import datetime


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


class GetBaseInfo(View):

    def get(self, request):
        # retrieve route list and available days
        es_shape_helper = ESShapeHelper()
        es_stop_helper = ESStopByRouteHelper()

        stop_dates = es_stop_helper.get_available_days()
        shape_dates = es_shape_helper.get_available_days()

        dates = list(set(stop_dates + shape_dates))
        dates.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

        stop_routes = es_stop_helper.get_route_list()
        shape_routes = es_shape_helper.get_route_list()

        routes = list(set(stop_routes + shape_routes))
        routes.sort()

        response = {
            'dates': dates,
            'routes': routes
        }

        return JsonResponse(response)


class MapHTML(View):
    """ load html map to show route polyline """

    def get(self, request):
        template = "shape/map.html"
        context = {}

        return render(request, template, context)
