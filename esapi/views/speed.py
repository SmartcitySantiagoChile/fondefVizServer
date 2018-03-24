# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from esapi.helper.speed import ESSpeedHelper
from esapi.helper.shape import ESShapeHelper
from esapi.errors import FondefVizError, ESQueryResultEmpty
from esapi.messages import SpeedVariationWithLessDaysMessage
from esapi.utils import check_operation_program
from esapi.messages import ExporterDataHasBeenEnqueuedMessage

from localinfo.helper import PermissionBuilder

from datamanager.helper import ExporterManager

import rqworkers.dataDownloader.csvhelper.helper as csv_helper
import datetime

hours = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
         "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
         "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
         "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
         "22:00", "22:30", "23:00", "23:30"]


class AvailableDays(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.get_available_days(valid_operator_list)

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):
        response = {}
        try:
            es_helper = ESSpeedHelper()
            valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
            available_days, op_dict = es_helper.get_available_routes(valid_operator_list)

            response['availableRoutes'] = available_days
            response['operatorDict'] = op_dict
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class MatrixData(View):

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        auth_route = params.get('authRoute', '')
        day_type = params.getlist('dayType[]', [])

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'segments': [],
            'matrix': [],
        }

        try:
            check_operation_program(start_date, end_date)
            es_shape_helper = ESShapeHelper()
            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_speed_data_query(auth_route, day_type, start_date, end_date,
                                                                     valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                shape = es_shape_helper.get_route_shape(auth_route, start_date, end_date)['points']
                route_points = [[s['latitude'], s['longitude']] for s in shape]
                limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]

                max_section = len(limits) - 1
                response['segments'] = list(range(max_section + 1))

                d_data = es_speed_helper.get_speed_data(auth_route, day_type, start_date, end_date, valid_operator_list)

                for hour in range(len(hours)):
                    route_segment_by_hour = []
                    for section in response['segments']:
                        speed, n_obs = d_data.get((section, hour), (-1, 0))
                        interval = 7
                        for i, bound in enumerate([0, 5, 10, 15, 20, 25, 30]):
                            if speed < bound:
                                interval = i
                                break
                        route_segment_by_hour.append([interval, speed, n_obs])
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

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        hour_period_from = params.get('hourPeriodFrom', None)
        hour_period_to = params.get('hourPeriodTo', None)
        day_type = params.getlist('dayType[]', None)

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'hours': hours,
            'data': [],
        }

        try:
            check_operation_program(start_date, end_date)
            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_ranking_data_query(start_date, end_date, hour_period_from,
                                                                       hour_period_to, day_type, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response['data'] = es_speed_helper.get_ranking_data(start_date, end_date, hour_period_from,
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
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        hour_period = params.get('period', [])
        day_type = params.getlist('dayType[]', [])

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'route': {
                'name': route,
                'points': [],
                'start_end': []
            },
            'speed': [],
        }

        try:
            check_operation_program(start_date, end_date)
            es_shape_helper = ESShapeHelper()
            es_speed_helper = ESSpeedHelper()

            if export_data:
                es_query = es_speed_helper.get_base_detail_ranking_data_query(route, start_date, end_date, hour_period,
                                                                              day_type, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.SPEED_MATRIX_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                shape = es_shape_helper.get_route_shape(route, start_date, end_date)['points']
                route_points = [[s['latitude'], s['longitude']] for s in shape]
                limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]
                start_end = list(zip(limits[:-1], limits[1:]))

                response['route']['start_end'] = start_end
                response['route']['points'] = route_points

                es_query = es_speed_helper.get_detail_ranking_data(route, start_date, end_date, hour_period, day_type,
                                                                   valid_operator_list)
                response['speed'] = self.process_data(es_query, limits)

        except ESQueryResultEmpty as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class SpeedVariation(View):

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
                    if value < 0:
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
        end_date = params.get('startDate', '')[:10]
        # startDate is the variable name that represents the date we need to calculate speed variation with respect to
        # previous days, that it's why we called end_date
        operator = int(params.get('operator', 0))
        user_route = params.get('userRoute', '')
        day_type = params.getlist('dayType[]', '')

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'variations': [],
            'routes': []
        }
        try:
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
