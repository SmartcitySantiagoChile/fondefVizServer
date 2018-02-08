# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search, A

from localinfo.models import TimePeriod

import datetime

# from errors import ESQueryDoesNotHaveParameters

from speed.esspeedhelper import ESSpeedHelper, ESShapeHelper


# elastic search index name
SHAPE_INDEX_NAME="shape"
daytypes = 'LSD'


class MatrixHTML(View):

    def get(self, request):
        template = "speed/matrix.html"
        self.es_helper = ESSpeedHelper()
        self.context = self.es_helper.make_multisearch_query_for_aggs(self.es_helper.get_base_params())

        return render(request, template, self.context)


class GetAvailableDays(View):

    def get(self, request):
        self.es_helper = ESSpeedHelper()
        available_days = self.es_helper.ask_for_available_days()

        response = {}
        response['availableDays'] = available_days

        return JsonResponse(response)


class GetAvailableRoutes(View):

    def get(self, request):
        self.es_helper = ESSpeedHelper()
        available_days, op_dict = self.es_helper.ask_for_available_routes()

        response = {}
        response['availableRoutes'] = available_days
        response['operatorDict'] = op_dict

        return JsonResponse(response)


class getMatrixData(View):

    def __init__(self):
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
        limits = [i for i,s in enumerate(shape) if s['segmentStart']==1]+[len(shape)-1]

        d_data = self.es_speed_helper.get_speed_data(route, day_type, start_date, end_date)

        max_section = len(limits)-1

        response = {
            'hours': ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"],
            'segments': list(range(max_section+1)),
            'matrix': [],
        }

        for hour in range(len(response['hours'])):
            segmentedRouteByHour = []
            for section in response['segments']:
                speed, n_obs = d_data.get((section, hour), (-1, 0))
                interval = 7
                for i, bound in enumerate([0, 5, 10, 15, 20, 25, 30]):
                    if speed < bound:
                        interval = i
                        break
                segmentedRouteByHour.append([interval, speed, n_obs])
            response['matrix'].append(segmentedRouteByHour)

        response['route'] = {'name': route, 'points': route_points, 'start_end': list(zip(limits[:-1], limits[1:]))}
        return JsonResponse(response, safe=False)


class LoadRankingView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}
        self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)

    def get(self, request):
        template = "velocity/ranking.html"

        return render(request, template, self.context)

class getLoadRankingData(View):

    def __init__(self):
        self.context = {}
        n_chunks = 6
        routes = self.getRouteList()
        indices = [int(i*len(routes)/n_chunks) for i in range(n_chunks+1)]
        self.chunks = [routes[i:j] for i,j in zip(indices[:-1], indices[1:])]

    def getRouteList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=SPEED_INDEX_NAME)
        esQuery = esQuery[:0]
        aggs = A('terms', field = 'route', size=2000)
        esQuery.aggs.bucket('unique_routes', aggs)

        routes = []
        for tag in esQuery.execute().aggregations.unique_routes.buckets:
            routes.append(tag.key)
        routes.sort()

        return routes

    def get(self, request):
        fromDate = request.GET.get('from', None)
        toDate = request.GET.get('to', None)
        fromPeriod = request.GET.get('periodFrom', None)
        toPeriod = request.GET.get('periodTo', None)
        dayType = request.GET.getlist('dayType[]', None)
        dayType = [daytypes.find(d[0]) for d in dayType]

        response = {
            'hours': ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"],
            'data': [],
        }

        client = settings.ES_CLIENT

        for chunk in self.chunks:
            esQuery = Search(using=client, index=SPEED_INDEX_NAME)
            esQuery = esQuery.filter('terms', route=chunk)
            esQuery = esQuery.filter('range', date={"gte": fromDate, "lte": toDate, "format": "dd/MM/yyyy"})
            esQuery = esQuery.filter('range', periodId={"gte": fromPeriod, "lte": toPeriod})
            if dayType:
                esQuery = esQuery.filter('terms', dayType=dayType)

            aggs0 = A('terms', field = 'merged', size=100000000)
            aggs0.metric('n_obs', 'sum', field='nObs')
            aggs0.metric('distance', 'sum', field='totalDistance')
            aggs0.metric('time', 'sum', field='totalTime')
            aggs0.metric('speed', 'bucket_script', script='params.d / params.t', buckets_path={'d': 'distance', 't': 'time'})
            esQuery.aggs.bucket('tuples', aggs0)

            r = esQuery.execute()

            for tup in r.aggregations.tuples.buckets:
                tha_key = tup.key
                tha_value = 3.6*tup.speed.value
                # if tha_value < 15:
                sep_key = tha_key.split('-')
                response['data'].append({
                    'route': sep_key[0],
                    'section': int(sep_key[1]),
                    'period': int(sep_key[2]),
                    'n_obs': tup.n_obs.value,
                    'distance': tup.distance.value,
                    'time': tup.time.value,
                    'speed': tha_value
                })

        response['data'].sort(key=lambda x: float(x['speed']))
        if len(response['data']) > 1000:
            response['data'] = response['data'][:1000]

        return JsonResponse(response, safe=False)

class getLoadSpeedByRoute(View):

    def __init__(self):
        self.context = {}

    def get(self, request):
        route = request.GET.get('route', None)
        fromDate = request.GET.get('from', None)
        toDate = request.GET.get('to', None)
        period = request.GET.get('period', None)
        dayType = request.GET.getlist('dayType[]', None)
        dayType = [daytypes.find(d[0]) for d in dayType]

        shape = getRouteShape(route, fromDate, toDate)
        route_points = [[s['latitude'], s['longitude']] for s in shape]
        limits = [i for i,s in enumerate(shape) if s['segmentStart']==1]+[len(shape)-1]

        response = {
            'route': {'name': route, 'points': route_points, 'start_end': list(zip(limits[:-1], limits[1:]))},
            'speed': [],
        }

        client = settings.ES_CLIENT

        esQuery = Search(using=client, index=SPEED_INDEX_NAME)
        esQuery = esQuery.filter('term', route=route)
        esQuery = esQuery.filter('range', date={"gte": fromDate, "lte": toDate, "format": "dd/MM/yyyy"})
        esQuery = esQuery.filter('term', periodId=int(period))
        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)

        aggs0 = A('terms', field = 'section', size=200)
        aggs0.metric('n_obs', 'sum', field='nObs')
        aggs0.metric('distance', 'sum', field='totalDistance')
        aggs0.metric('time', 'sum', field='totalTime')
        aggs0.metric('speed', 'bucket_script', script='params.d / params.t', buckets_path={'d': 'distance', 't': 'time'})
        esQuery.aggs.bucket('sections', aggs0)

        r = esQuery.execute()

        aux_data = {}
        for sec in r.aggregations.sections.buckets:
            key = sec.key
            aux_data[key] = 3.6*sec.speed.value

        for i in range(len(limits)-1):
            sp = aux_data.get(i, -1)
            interval = 6
            for i, bound in enumerate([0, 15, 19, 21, 23, 30]):
                if sp < bound:
                    interval = i
                    break
            response['speed'].append(interval)

        # return JsonResponse(esQuery.to_dict(), safe=False)
        return JsonResponse(response, safe=False)

class getLoadSpeedVariationView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}
        self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        self.context['routes'] = self.getRouteList()

    def getRouteList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT
        esQuery = Search(using=client, index=SPEED_INDEX_NAME)
        esQuery = esQuery[:0]
        aggs = A('terms', field = 'route', size=2000)
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
        esQuery = esQuery.filter('range', date={"gte": (theDate-datetime.timedelta(days=31)).strftime("%d/%m/%Y"), "lte": theDate.strftime("%d/%m/%Y"), "format": "dd/MM/yyyy"})
        if routes:
            esQuery = esQuery.filter('terms', route=routes)
        if dayType:
            esQuery = esQuery.filter('terms', dayType=dayType)

        aggs0 = A('terms', field = 'route', size=2000)
        aggs1 = A('terms', field = 'periodId', size=50)
        aggs2 = A('range', field = 'date', format='dd/MM/yyyy', ranges = [{'to': theDate.strftime("%d/%m/%Y")}, {'from': theDate.strftime("%d/%m/%Y")}])

        aggs2.metric('distance', 'sum', field='totalDistance')
        aggs2.metric('time', 'sum', field='totalTime')
        aggs2.metric('n_obs', 'sum', field='nObs')
        aggs2.metric('stats', 'extended_stats', field='speed')
        aggs2.metric('speed', 'bucket_script', script='params.d / params.t', buckets_path={'d': 'distance', 't': 'time'})
        esQuery.aggs.bucket('routes', aggs0).bucket('periods', aggs1).bucket('days', aggs2)

        print(str(esQuery.to_dict()).replace('\'','"'))
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
                    if day.key[0]=='*' and day.time.value > 0:
                        mes = 3.6*day.speed.value
                        nob_mes = day.n_obs.value
                        mes_stats = day.stats.std_deviation
                    elif day.key[-1]=='*' and day.time.value > 0:
                        dia = 3.6*day.speed.value
                        nob_dia = day.n_obs.value
                        dia_stats = day.stats.std_deviation
                perc = None
                if mes != 0:
                    perc = 100*dia/mes
                else:
                    perc = -1
                aux_data[(r_key, p_key)] = (perc, dia, mes, nob_dia, nob_mes, dia_stats, mes_stats)

        data = []
        l_routes = sorted(list(l_routes))
        for per in range(48):
            p_data = []
            for rou in l_routes:
                value, v_dia, v_mes, nob_dia, nob_mes, dia_stats, mes_stats = aux_data.get((rou,per), [None, 0, 0, 0, 0, 0, 0])
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
