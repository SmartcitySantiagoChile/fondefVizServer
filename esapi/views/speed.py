# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from esapi.helper.speed import ESSpeedHelper
from esapi.helper.shape import ESShapeHelper
from esapi.errors import ESQueryResultEmpty

import datetime

hours = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
         "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
         "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
         "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
         "22:00", "22:30", "23:00", "23:30"]


class AvailableDays(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        available_days = es_helper.ask_for_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        available_days, op_dict = es_helper.ask_for_available_routes()

        response = {
            'availableRoutes': available_days,
            'operatorDict': op_dict
        }

        return JsonResponse(response)


class MatrixData(View):

    def __init__(self):
        super(MatrixData, self).__init__()
        self.context = {}
        self.es_shape_helper = ESShapeHelper()
        self.es_speed_helper = ESSpeedHelper()

    def get(self, request):
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        route = request.GET.get('authRoute', None)
        day_type = request.GET.getlist('dayType[]', None)

        shape = self.es_shape_helper.get_route_shape(route, start_date, end_date)
        route_points = [[s['latitude'], s['longitude']] for s in shape]
        limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]

        max_section = len(limits) - 1

        response = {
            'segments': list(range(max_section + 1)),
            'matrix': [],
        }

        try:
            d_data = self.es_speed_helper.ask_for_speed_data(route, day_type, start_date, end_date)

            for hour in range(len(hours)):
                segmented_route_by_hour = []
                for section in response['segments']:
                    speed, n_obs = d_data.get((section, hour), (-1, 0))
                    interval = 7
                    for i, bound in enumerate([0, 5, 10, 15, 20, 25, 30]):
                        if speed < bound:
                            interval = i
                            break
                    segmented_route_by_hour.append([interval, speed, n_obs])
                response['matrix'].append(segmented_route_by_hour)

            response['route'] = {
                'name': route,
                'points': route_points,
                'start_end': list(zip(limits[:-1], limits[1:]))
            }
        except ESQueryResultEmpty as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class RankingData(View):

    def get(self, request):
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        hour_period_from = request.GET.get('hourPeriodFrom', None)
        hour_period_to = request.GET.get('hourPeriodTo', None)
        day_type = request.GET.getlist('dayType[]', None)

        response = {
            'hours': hours,
            'data': [],
        }

        try:
            es_helper = ESSpeedHelper()
            response['data'] = es_helper.ask_for_ranking_data(start_date, end_date, hour_period_from, hour_period_to,
                                                              day_type)

            if len(response['data']) > 1000:
                response['data'] = response['data'][:1000]
        except ESQueryResultEmpty as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


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

    def get(self, request):
        route = request.GET.get('authRoute', '')
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        hour_period = request.GET.get('period', [])
        day_type = request.GET.getlist('dayType[]', [])

        response = {
            'route': {
                'name': route,
                'points': [],
                'start_end': []
            },
            'speed': [],
        }

        try:
            es_helper = ESShapeHelper()
            shape = es_helper.get_route_shape(route, start_date, end_date)
            route_points = [[s['latitude'], s['longitude']] for s in shape]
            limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]
            start_end = list(zip(limits[:-1], limits[1:]))

            response['route']['start_end'] = start_end
            response['route']['points'] = route_points

            es_helper = ESSpeedHelper()
            es_query = es_helper.ask_for_detail_ranking_data(route, start_date, end_date, hour_period, day_type)
            response['speed'] = self.process_data(es_query, limits)

        except ESQueryResultEmpty as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class SpeedVariation(View):

    def get(self, request):
        _date = request.GET.get('startDate', None)
        the_date = datetime.datetime.strptime(_date, '%Y-%m-%d')
        routes = request.GET.getlist('route[]', None)
        day_type = request.GET.getlist('dayType[]', None)

        es_helper = ESSpeedHelper()
        r = es_helper.ask_for_speed_variation(the_date, day_type, routes)

        aux_data = {}
        l_routes = set()
        for rou in r.execute().aggregations.routes.buckets:
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
                        mes = 3.6 * day.speed.value
                        nob_mes = day.n_obs.value
                        mes_stats = day.stats.std_deviation
                    elif day.key[-1] == '*' and day.time.value > 0:
                        dia = 3.6 * day.speed.value
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
        response = {
            'variations': data,
            'routes': l_routes
        }

        return JsonResponse(response, safe=False)
