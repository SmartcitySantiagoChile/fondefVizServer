# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, A

from localinfo.models import TimePeriod

import datetime

from errors import ESQueryResultEmpty

from speed.esspeedhelper import ESSpeedHelper, ESShapeHelper


class SpeedVariationHTML(View):

    def get(self, request):
        template = "speed/variation.html"

        context = {}
        context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        es_helper = ESSpeedHelper()
        context['routes'] = es_helper.get_route_list()

        return render(request, template, context)


class GetSpeedVariationData(View):
    def __init__(self):
        self.context = {}

    def get(self, request):
        SPEED_INDEX_NAME = 'speed'

        _date = request.GET.get('date', None)
        theDate = datetime.datetime.strptime(_date, '%d/%m/%Y')
        routes = request.GET.getlist('route[]', None)
        dayType = request.GET.getlist('dayType[]', None)
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
