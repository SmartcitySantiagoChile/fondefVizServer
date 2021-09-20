import datetime

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import FondefVizError, ESQueryResultEmpty, ESQueryDateParametersDoesNotExist
from esapi.helper.shape import ESShapeHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from esapi.messages import SpeedVariationWithLessDaysMessage
from esapi.utils import check_operation_program, get_dates_from_request
from localinfo.helper import PermissionBuilder, get_calendar_info, get_op_routes_dict, \
    get_opprogram_list_for_select_input

hours = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
         "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
         "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
         "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
         "22:00", "22:30", "23:00", "23:30"]


class AvailableDays(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)
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
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        try:
            es_helper = ESSpeedHelper()
            valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)
            available_routes, op_dict = es_helper.get_available_routes(valid_operator_list, start_date, end_date)
            available_operators = available_routes.keys()
            op_dict = [operator_dict for operator_dict in op_dict if operator_dict["value"] in available_operators]
            response['availableRoutes'] = available_routes
            response['operatorDict'] = op_dict
            response['routesDict'] = get_op_routes_dict()
            response['opProgramDates'] = get_opprogram_list_for_select_input(to_dict=True)

        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class MatrixData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MatrixData, self).dispatch(request, *args, **kwargs)

    def process_request(self, request, params, export_data=False):

        dates = get_dates_from_request(request, export_data)
        auth_route = params.get('authRoute', '')
        day_type = params.getlist('dayType[]', [])

        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)

        response = {
            'segments': [],
            'matrix': [],
        }

        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            check_operation_program(dates[0][0], dates[-1][-1])

            es_shape_helper = ESShapeHelper()
            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_speed_data_query(auth_route, day_type, dates,
                                                                     valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                shape = es_shape_helper.get_route_shape(auth_route, dates)['points']
                route_points = [[s['latitude'], s['longitude']] for s in shape]
                limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]
                max_section = len(limits) - 1
                response['segments'] = list(range(max_section + 1))
                d_data = es_speed_helper.get_speed_data(auth_route, day_type, dates, valid_operator_list)
                for hour in range(len(hours)):
                    route_segment_by_hour = []
                    for section in response['segments']:
                        speed, n_obs, distance, time = d_data.get((section, hour), (-1, 0, 0, 0))
                        interval = 8
                        for i, bound in enumerate([0, 5, 7.5, 10, 15, 20, 25, 30]):
                            if speed < bound:
                                interval = i
                                break
                        route_segment_by_hour.append([interval, speed, n_obs, distance, time])
                    response['matrix'].append(route_segment_by_hour)
                response['route'] = {
                    'name': auth_route,
                    'points': route_points,
                    'start_end': list(zip(limits[:-1], limits[1:]))
                }
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class RankingData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RankingData, self).dispatch(request, *args, **kwargs)

    def process_request(self, request, params, export_data=False):
        dates = get_dates_from_request(request, export_data)
        hour_period_from = params.get('hourPeriodFrom', None)
        hour_period_to = params.get('hourPeriodTo', None)
        day_type = params.getlist('dayType[]', None)
        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)

        response = {
            'hours': hours,
            'data': [],
        }

        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            check_operation_program(dates[0][0], dates[-1][-1])

            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_ranking_data_query(dates, hour_period_from,
                                                                       hour_period_to, day_type, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response['data'] = es_speed_helper.get_ranking_data(dates, hour_period_from,
                                                                    hour_period_to,
                                                                    day_type, valid_operator_list)

                if len(response['data']) > 1000:
                    response['data'] = response['data'][:1000]
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class SpeedByRoute(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SpeedByRoute, self).dispatch(request, *args, **kwargs)

    def process_data(self, es_query, limits):
        aux_data = {}
        for sec in es_query.execute().aggregations.sections.buckets:
            key = sec.key
            aux_data[key] = 3.6 * sec.speed.value

        result = []
        for i in range(len(limits) - 1):
            sp = aux_data.get(i, -1)
            interval = 6
            for j, bound in enumerate([0, 15, 19, 21, 23, 30]):
                if sp < bound:
                    interval = j
                    break
            result.append(interval)

        return result

    def process_request(self, request, params, export_data=False):
        route = params.get('authRoute', '')
        dates = get_dates_from_request(request, export_data)
        hour_period = params.get('period', [])
        day_type = params.getlist('dayType[]', [])

        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)

        response = {
            'route': {
                'name': route,
                'points': [],
                'start_end': []
            },
            'speed': [],
        }

        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            check_operation_program(dates[0][0], dates[-1][-1])

            es_shape_helper = ESShapeHelper()
            es_speed_helper = ESSpeedHelper()
            if export_data:
                es_query = es_speed_helper.get_base_detail_ranking_data_query(route, dates, hour_period,
                                                                              day_type, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                shape = es_shape_helper.get_route_shape(route, dates)['points']
                route_points = [[s['latitude'], s['longitude']] for s in shape]
                limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]
                start_end = list(zip(limits[:-1], limits[1:]))

                response['route']['start_end'] = start_end
                response['route']['points'] = route_points

                es_query = es_speed_helper.get_detail_ranking_data(route, dates, hour_period, day_type,
                                                                   valid_operator_list)
                response['speed'] = self.process_data(es_query, limits)

        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class SpeedVariation(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SpeedVariation, self).dispatch(request, *args, **kwargs)

    def transform_data(self, es_query):
        aux_data = {}
        l_routes = set()

        result = es_query.execute().aggregations.routes.buckets

        if not result:
            raise ESQueryResultEmpty()

        for rou in result:
            r_key = rou.key
            l_routes.add(r_key)
            for per in rou.periods.buckets:
                p_key = per.key
                mes = 0
                nob_mes = 0
                mes_stats = 0
                dia = 0
                nob_dia = 0
                dia_stats = 0
                for day in per.days.buckets:
                    if day.key[0] == '*' and day.time.value > 0:
                        mes = day.speed.value
                        nob_mes = day.n_obs.value
                        mes_stats = day.stats.std_deviation
                    elif day.key[-1] == '*' and day.time.value > 0:
                        dia = day.speed.value
                        nob_dia = day.n_obs.value
                        dia_stats = day.stats.std_deviation

                if mes != 0:
                    perc = 100 * dia / mes
                else:
                    perc = -1
                aux_data[(r_key, p_key)] = (perc, dia, mes, nob_dia, nob_mes, dia_stats, mes_stats)

        data = []
        l_routes = sorted(list(l_routes))
        for per in range(48):
            p_data = []
            for rou in l_routes:
                value, v_dia, v_mes, nob_dia, nob_mes, dia_stats, mes_stats = aux_data.get((rou, per),
                                                                                           [None, 0, 0, 0, 0, 0, 0])
                color = 7
                if aux_data:
                    if not value or value < 0:
                        color = 0
                    elif value == 0:
                        color = 8
                        value = None
                    elif value <= 30:
                        color = 1
                    elif value <= 45:
                        color = 2
                    elif value <= 60:
                        color = 3
                    elif value <= 75:
                        color = 4
                    elif value <= 90:
                        color = 5
                    elif value <= 100:
                        color = 6
                    else:
                        color = 7
                p_data.append([color, value, v_dia, v_mes, nob_dia, nob_mes, dia_stats, mes_stats])
            data.append(p_data)

        return data, l_routes

    def process_request(self, request, params, export_data=False):
        dates = get_dates_from_request(request, export_data)
        # startDate is the variable name that represents the date we need to calculate speed variation with respect to
        # previous days, that it's why we called end_date
        operator = int(params.get('operator', 0))
        user_route = params.get('userRoute', '')
        day_type = params.getlist('dayType[]', '')

        valid_operator_list = PermissionBuilder.get_valid_operator_id_list(request.user)

        response = {
            'variations': [],
            'routes': []
        }
        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            end_date = dates[0][0]

            date_format = "%Y-%m-%d"

            most_recent_op_program_date = ESShapeHelper().get_most_recent_operation_program_date(end_date)
            most_recent_op_program_date_obj = datetime.datetime.strptime(most_recent_op_program_date, date_format)
            end_date_obj = datetime.datetime.strptime(end_date, date_format)
            days = 31
            if (end_date_obj - most_recent_op_program_date_obj).days < days:
                days = (end_date_obj - most_recent_op_program_date_obj).days
                response['status'] = SpeedVariationWithLessDaysMessage(days, most_recent_op_program_date). \
                    get_status_response()

            start_date = (end_date_obj - datetime.timedelta(days=days)).strftime(date_format)
            check_operation_program(start_date, end_date)

            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_variation_speed_query(start_date, end_date, day_type, user_route,
                                                                          operator, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_speed_helper.get_speed_variation_data(start_date, end_date, day_type, user_route,
                                                                    operator, valid_operator_list)
                response['variations'], response['routes'] = self.transform_data(es_query)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
