from collections import defaultdict
from datetime import datetime, date, timedelta

from django.http import JsonResponse
from django.views import View

from esapi.errors import FondefVizError, ESQueryRouteParameterDoesNotExist, ESQueryDateParametersDoesNotExist
from esapi.helper.profile import ESProfileHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from localinfo.helper import PermissionBuilder, get_valid_time_period_date, get_periods_dict, \
    get_operator_list_for_select_input
from localinfo.models import OPProgram, OPDictionary


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
        op_dates = list(map(lambda x: x.strftime('%Y-%m-%d'),
                            OPProgram.objects.order_by('-valid_from').values_list('valid_from', flat=True)))
        op_dates_dict = {date_id: date_obj.strftime('%Y-%m-%d') for date_id, date_obj in
                         OPProgram.objects.values_list('id', 'valid_from')}
        authority_periods = get_periods_dict()
        operator_dict = get_operator_list_for_select_input(to_dict=True)

        dates_periods_dict = {}
        for op_date in op_dates:
            dates_periods_dict[op_date] = get_valid_time_period_date([op_date])[1]

        op_routes_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: dict))))
        for op_dict_obj in OPDictionary.objects.order_by('op_program_id', 'operator', 'user_route_code',
                                                         'auth_route_code'). \
                values_list('op_program_id', 'operator', 'user_route_code', 'auth_route_code', 'op_route_code'):
            op_routes_dict[op_dates_dict[op_dict_obj[0]]][operator_dict[op_dict_obj[1]]][op_dict_obj[2]][
                op_dict_obj[3]] = op_dict_obj[4]

        response = {
            'dates': op_dates,
            'dates_periods_dict': dates_periods_dict,
            'periods': authority_periods,
            'op_routes_dict': op_routes_dict
        }

        return JsonResponse(response)


class GetUserRoutesByOP(View):

    def get(self, request):
        end_date = '2050-12-31'
        es_shape_helper = ESShapeHelper()
        es_stop_helper = ESStopByRouteHelper()
        stop_dates = es_stop_helper.get_available_days()
        shape_dates = es_shape_helper.get_available_days()
        dates = list(set(stop_dates + shape_dates))
        dates.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

        start_date = request.GET.get("op_program", '')
        index = dates.index(start_date)
        if index < len(dates) - 1:
            end_date = dates[index + 1]
            end_date = date.fromisoformat(end_date) - timedelta(days=1)
            end_date = end_date.isoformat()

        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)
        es_helper = ESProfileHelper()

        available_routes, op_dict = es_helper.get_available_routes(valid_operator_list, start_date=start_date,
                                                                   end_date=end_date)
        user_routes = defaultdict(list)
        for key in available_routes:
            for value in available_routes[key]:
                user_routes[value].extend(available_routes[key][value])
        response = {
            'user_routes': user_routes,
        }
        return JsonResponse(response)
