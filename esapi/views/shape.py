# -*- coding: utf-8 -*-


from datetime import datetime

from django.http import JsonResponse
from django.views import View

from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.profile import ESProfileHelper
from localinfo.helper import PermissionBuilder, get_valid_time_period_date, get_timeperiod_list_for_select_input, \
    get_periods_dict, get_op_routes_dict


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

        periods = get_periods_dict()

        dates_periods_dict = {}
        for date in dates:
            dates_periods_dict[date] = get_valid_time_period_date([date])[1]

        stop_routes = es_stop_helper.get_route_list()
        shape_routes = es_shape_helper.get_route_list()

        routes = list(set(stop_routes + shape_routes))
        routes.sort()

        es_helper = ESProfileHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_routes, op_dict = es_helper.get_available_routes(valid_operator_list)
        user_routes = {}
        for key in available_routes:
            for value in available_routes[key]:
                user_routes[value] = available_routes[key][value]
        op_routes_dict = get_op_routes_dict(key='auth_route_code', answer='op_route_code')
        response = {
            'dates': dates,
            'routes': routes,
            'user_routes': user_routes,
            'dates_periods_dict': dates_periods_dict,
            'periods': periods,
            'op_routes_dict': op_routes_dict
        }

        return JsonResponse(response)
