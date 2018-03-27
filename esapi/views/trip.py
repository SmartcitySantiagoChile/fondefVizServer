# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

from esapi.helper.trip import ESTripHelper
from esapi.errors import FondefVizError, ESQueryResultEmpty
from esapi.messages import ExporterDataHasBeenEnqueuedMessage

from datamanager.helper import ExporterManager

import rqworkers.dataDownloader.csvhelper.helper as csv_helper


class ResumeData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ResumeData, self).dispatch(request, *args, **kwargs)

    def process_data(self, data_dict):

        return data_dict

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        origin_zones = map(lambda x: int(x), params.getlist('origin[]', []))
        destination_zones = map(lambda x: int(x), params.getlist('destination[]', []))

        es_helper = ESTripHelper()

        response = {}

        try:
            if export_data:
                es_query = es_helper.get_base_resume_data_query(start_date, end_date, day_types, periods, origin_zones,
                                                                destination_zones)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query_dict = es_helper.get_resume_data(start_date, end_date, day_types, periods, origin_zones,
                                                          destination_zones)
                response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class MapData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MapData, self).dispatch(request, *args, **kwargs)

    def process_data(self, data_dict):

        return data_dict

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('boardingPeriod[]', [])

        es_helper = ESTripHelper()

        sectors = {
            'Lo Barnechea': [202, 642],
            'Centro': [267, 276, 285, 286],
            'Providencia': [175, 176, 179],
            'Las Condes': [207, 215, 216],
            'Vitacura': [191, 192, 193, 195, 196],
            'Quilicura': [557, 831]
        }

        KPIs = [
            {'id': 'tviaje', 'text': 'Tiempo de viaje'},
            {'id': 'distancia_ruta', 'text': 'Distancia en ruta'},
            {'id': 'distancia_eucl', 'text': 'Distancia euclideana'},
            {'id': 'n_etapas', 'text': 'Número de etapas'},
            {'id': 'count', 'text': 'Cantidad de datos'}
        ]

        response = {
            # 777 zones for each sector
            'sectors': sectors,
            'KPIs': KPIs
        }

        try:
            if export_data:
                es_query = es_helper.get_base_map_data_query(start_date, end_date, day_types, periods, sectors)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query_dict = es_helper.get_map_data(start_date, end_date, day_types, periods, sectors)
                response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class AvailableDays(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def get(self, request):
        es_helper = ESTripHelper()
        available_days = es_helper.get_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class LargeTravelData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LargeTravelData, self).dispatch(request, *args, **kwargs)

    def process_data(self, data):
        return data

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        stages = params.getlist('stages[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_large_travel_data_query(start_date, end_date, day_types, periods, stages)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query_dict = es_helper.get_large_travel_data(start_date, end_date, day_types, periods, stages)
                response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class FromToMapData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FromToMapData, self).dispatch(request, *args, **kwargs)

    def process_data(self, data):
        return data

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        minutes = params.getlist('halfHour[]', [])
        stages = params.getlist('stages[]', [])
        modes = params.getlist('modes[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_from_to_map_data_query(start_date, end_date, day_types, periods, minutes,
                                                                     stages, modes)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query_dict = es_helper.get_from_to_map_data(start_date, end_date, day_types, periods, minutes,
                                                               stages, modes)
                response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST)


class StrategiesData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StrategiesData, self).dispatch(request, *args, **kwargs)

    def process_data(self, es_query):
        subway = 'METRO'
        train = 'METROTREN'

        strategies_tuples = defaultdict(lambda: {'travels': []})

        for hit in es_query.scan():
            _data = hit.to_dict()
            t = ''
            if _data['tipo_transporte_1'] == 2:
                t += subway
            elif _data['tipo_transporte_1'] == 4:
                t += train
            else:
                t += _data['srv_1']
            t += ' | '

            if _data['tipo_transporte_2'] == 2:
                t += subway
            elif _data['tipo_transporte_2'] == 4:
                t += train
            else:
                t += _data['srv_2']
            t += ' | '

            if _data['tipo_transporte_3'] == 2:
                t += subway
            elif _data['tipo_transporte_3'] == 4:
                t += train
            else:
                t += _data['srv_3']
            t += ' | '

            if _data['tipo_transporte_4'] == 2:
                t += subway
            elif _data['tipo_transporte_4'] == 4:
                t += train
            else:
                t += _data['srv_4']

            strategies_tuples[t]['travels'].append(_data['id'])

        return strategies_tuples

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('daytypes[]', [])
        periods = params.getlist('period[]', [])
        minutes = params.getlist('halfHour[]', [])
        origin_zone = params.getlist('origins[]', [])
        destination_zone = params.getlist('destinations[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_strategies_data_query(start_date, end_date, day_types, periods, minutes,
                                                                    origin_zone, destination_zone)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_helper.get_strategies_data(start_date, end_date, day_types, periods, minutes,
                                                         origin_zone, destination_zone)
                response['strategies'] = self.process_data(es_query)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class TransfersData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TransfersData, self).dispatch(request, *args, **kwargs)

    def process_data(self, es_query):
        result = es_query.execute().aggregations
        answer = defaultdict(lambda: defaultdict(lambda: 0))

        for step in [result.first_transfer, result.second_transfer, result.third_transfer]:
            for from_bucket in step.route_from.buckets:
                for to_bucket in from_bucket.route_to.buckets:
                    answer[from_bucket.key][to_bucket.key] += to_bucket.doc_count

        for from_bucket in result.fourth_transfer.route_from.buckets:
            answer[from_bucket.key]['-'] += from_bucket.doc_count

        if not answer:
            raise ESQueryResultEmpty()

        # print(str(es_query.to_dict()).replace("u'", "\"").replace("'", "\""))
        return {
            # 'result': result.to_dict(),
            'data': answer
        }

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        auth_stop_code = params.get('stopCode', 'L-22-11-30-SN')
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        half_hours = params.getlist('halfHour[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_transfers_data_query(start_date, end_date, auth_stop_code, day_types,
                                                                   periods, half_hours)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_helper.get_transfers_data(start_date, end_date, auth_stop_code, day_types, periods,
                                                        half_hours)[:0]
                response.update(self.process_data(es_query))
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
