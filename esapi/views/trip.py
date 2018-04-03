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
                histogram, indicators = es_helper.get_resume_data(start_date, end_date, day_types, periods,
                                                                  origin_zones, destination_zones)
                histogram, indicators = es_helper.make_multisearch_query_for_aggs(histogram, indicators)

                if histogram.hits.total == 0:
                    raise ESQueryResultEmpty

                response['histogram'] = histogram.to_dict()
                response['indicators'] = indicators.to_dict()
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
                es_query = es_helper.get_map_data(start_date, end_date, day_types, periods, sectors)
                response['map'] = es_helper.make_multisearch_query_for_aggs(es_query, flat=True).to_dict()
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

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        stages = params.getlist('stages[]', [])
        origin_or_destination = params.get('originOrDestination', 'origin')

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_large_travel_data_query(start_date, end_date, day_types, periods, stages)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_helper.get_large_travel_data(start_date, end_date, day_types, periods, stages,
                                                           origin_or_destination)
                response['large'] = es_helper.make_multisearch_query_for_aggs(es_query, flat=True).to_dict()
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

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('dayType[]', [])
        periods = params.getlist('period[]', [])
        minutes = params.getlist('halfHour[]', [])
        stages = params.getlist('stages[]', [])
        transport_modes = params.getlist('transportModes[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_from_to_map_data_query(start_date, end_date, day_types, periods, minutes,
                                                                     stages, transport_modes)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                queries = es_helper.get_from_to_map_data(start_date, end_date, day_types, periods, minutes, stages,
                                                         transport_modes)
                origin_zone, destination_zone = es_helper.make_multisearch_query_for_aggs(*queries)

                if origin_zone.hits.total == 0 or destination_zone.hits.total == 0:
                    raise ESQueryResultEmpty

                response['origin_zone'] = origin_zone.to_dict()
                response['destination_zone'] = destination_zone.to_dict()
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

        trips = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
        for first in es_query.execute().aggregations.strategies.buckets:
            first_type = first.additionalInfo.hits.hits[0]['_source']['tipo_transporte_1']
            first_mode = subway if first_type == 2 else train if first_type == 4 else first.key
            for second in first.second.buckets:
                second_type = second.additionalInfo.hits.hits[0]['_source']['tipo_transporte_2']
                second_mode = subway if second_type == 2 else train if second_type == 4 else second.key
                for third in second.third.buckets:
                    third_type = third.additionalInfo.hits.hits[0]['_source']['tipo_transporte_3']
                    third_mode = subway if third_type == 2 else train if third_type == 4 else third.key
                    for fourth in third.fourth.buckets:
                        fourth_type = fourth.additionalInfo.hits.hits[0]['_source']['tipo_transporte_4']
                        fourth_mode = subway if fourth_type == 2 else train if fourth_type == 4 else fourth.key

                        # TODO: expansion factor es cero, consultar con mauricio
                        value = fourth.expansion_factor.value if fourth.expansion_factor.value != 0 else fourth.doc_count
                        trips[first_mode][second_mode][third_mode][fourth_mode] += value

        return {
            'trips': trips
        }

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

        for step in [result.first_transfer, result.second_transfer, result.third_transfer,
                     result.first_transfer_to_subway, result.second_transfer_to_subway,
                     result.third_transfer_to_subway]:
            for from_bucket in step.route_from.buckets:
                for to_bucket in from_bucket.route_to.buckets:
                    answer[to_bucket.key][from_bucket.key] += to_bucket.expansion_factor.value

        for step in [result.first_transfer_is_end, result.second_transfer_is_end, result.third_transfer_is_end]:
            for from_bucket in step.route_from.buckets:
                for to_bucket in from_bucket.route_to.buckets:
                    end = to_bucket.key
                    if end == '-':
                        end = 'end'
                    answer[end][from_bucket.key] += to_bucket.expansion_factor.value

        for from_bucket in result.fourth_transfer_is_end.route_from.buckets:
            answer['end'][from_bucket.key] += from_bucket.expansion_factor.value

        if not answer:
            raise ESQueryResultEmpty()

        return {
            'data': answer
        }

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        auth_stop_code = params.get('stopCode', '')
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
