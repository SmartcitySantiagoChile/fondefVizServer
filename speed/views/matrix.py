# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from errors import ESQueryParametersDoesNotExist, ESQueryResultEmpty

from speed.esspeedhelper import ESSpeedHelper, ESShapeHelper


class MatrixHTML(View):

    def get(self, request):
        template = "speed/matrix.html"
        es_helper = ESSpeedHelper()
        context = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        return render(request, template, context)


class GetAvailableDays(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        available_days = es_helper.ask_for_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class GetAvailableRoutes(View):

    def get(self, request):
        es_helper = ESSpeedHelper()
        available_days, op_dict = es_helper.ask_for_available_routes()

        response = {
            'availableRoutes': available_days,
            'operatorDict': op_dict
        }

        return JsonResponse(response)


class GetMatrixData(View):

    def __init__(self):
        super(GetMatrixData, self).__init__()
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
            'hours': ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
                      "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                      "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
                      "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
                      "22:00", "22:30", "23:00", "23:30"],
            'segments': list(range(max_section + 1)),
            'matrix': [],
        }

        try:
            d_data = self.es_speed_helper.get_speed_data(route, day_type, start_date, end_date)

            for hour in range(len(response['hours'])):
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

            response['route'] = {'name': route, 'points': route_points, 'start_end': list(zip(limits[:-1], limits[1:]))}
        except ESQueryResultEmpty as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)
