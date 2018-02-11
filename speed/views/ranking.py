# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, A

from localinfo.models import TimePeriod

import datetime

from esapi.errors import ESQueryResultEmpty

from speed.esspeedhelper import ESSpeedHelper, ESShapeHelper


class RankingHTML(View):

    def get(self, request):
        template = "speed/ranking.html"
        es_helper = ESSpeedHelper()
        context = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        return render(request, template, context)


class GetRankingData(View):

    def get(self, request):
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        hour_period_from = request.GET.get('hourPeriodFrom', None)
        hour_period_to = request.GET.get('hourPeriodTo', None)
        day_type = request.GET.getlist('dayType[]', None)

        response = {
            'hours': ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00",
                      "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                      "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
                      "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
                      "22:00", "22:30", "23:00", "23:30"],
            'data': [],
        }

        try:
            es_helper = ESSpeedHelper()
            response['data'] = es_helper.get_ranking_data(start_date, end_date, hour_period_from, hour_period_to, day_type)

            if len(response['data']) > 1000:
                response['data'] = response['data'][:1000]
        except ESQueryResultEmpty as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)


class GetSpeedByRoute(View):

    def get(self, request):
        route = request.GET.get('route', None)
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        hour_period = request.GET.get('period', None)
        day_type = request.GET.getlist('dayType[]', None)

        es_helper = ESShapeHelper()
        shape = es_helper.get_route_shape(route, start_date, end_date)
        route_points = [[s['latitude'], s['longitude']] for s in shape]
        limits = [i for i, s in enumerate(shape) if s['segmentStart'] == 1] + [len(shape) - 1]

        response = {
            'route': {
                'name': route,
                'points': route_points,
                'start_end': list(zip(limits[:-1], limits[1:]))
            },
            'speed': [],
        }

        es_helper = ESSpeedHelper()
        response['speed'] = es_helper.get_detail_ranking_data(route, start_date, end_date, hour_period, day_type,
                                                              limits)

        # return JsonResponse(esQuery.to_dict(), safe=False)
        return JsonResponse(response, safe=False)


class getLoadSpeedVariationView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context = {}
        self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        self.context['routes'] = self.getRouteList()

    def getRouteList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=SPEED_INDEX_NAME)
        esQuery = esQuery[:0]
        aggs = A('terms', field='route', size=2000)
        esQuery.aggs.bucket('unique_routes', aggs)

        routes = []
        for tag in esQuery.execute().aggregations.unique_routes.buckets:
            routes.append(tag.key)
        routes.sort()

        return routes

    def get(self, request):
        template = "velocity/variation.html"

        return render(request, template, self.context)


class getLoadSpeedVariationData(View):
    def __init__(self):
        self.context = {}

    def get(self, request):
        SPEED_INDEX_NAME = 'speed'

        _date = request.GET.get('date', None)
        theDate = datetime.datetime.strptime(_date, '%d/%m/%Y')
        routes = request.GET.getlist('route[]', None)
        dayType = request.GET.getlist('dayType[]', None)
        dayType = [daytypes.find(d[0]) for d in dayType]
        client = settings.ES_CLIENT

        esQuery = Search(using=client, index=SPEED_INDEX_NAME)
        esQuery = esQuery.filter('range', date={"gte": (theDate - datetime.timedelta(days=31)).strftime("%d/%m/%Y"),
                                                "lte": theDate.strftime("%d/%m/%Y"), "format": "dd/MM/yyyy"})
        if routes:
            esQuery = esQuery.filter('terms', route=routes)
        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)

        aggs0 = A('terms', field='route', size=2000)
        aggs1 = A('terms', field='periodId', size=50)
        aggs2 = A('range', field='date', format='dd/MM/yyyy',
                  ranges=[{'to': theDate.strftime("%d/%m/%Y")}, {'from': theDate.strftime("%d/%m/%Y")}])

        aggs2.metric('distance', 'sum', field='totalDistance')
        aggs2.metric('time', 'sum', field='totalTime')
        aggs2.metric('n_obs', 'sum', field='nObs')
        aggs2.metric('stats', 'extended_stats', field='speed')
        aggs2.metric('speed', 'bucket_script', script='params.d / params.t',
                     buckets_path={'d': 'distance', 't': 'time'})
        esQuery.aggs.bucket('routes', aggs0).bucket('periods', aggs1).bucket('days', aggs2)

        # print(str(esQuery.to_dict()).replace('\'', '"'))
        r = esQuery.execute()

        aux_data = {}
        l_routes = set()
        for rou in r.aggregations.routes.buckets:
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
                perc = None
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
