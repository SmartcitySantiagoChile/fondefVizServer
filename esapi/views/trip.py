# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

from esapi.helper.trip import ESTripHelper
from esapi.helper.stop import ESStopHelper
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
        origin_zones = params.getlist('originZones[]', [])
        destination_zones = params.getlist('destinationZones[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_from_to_map_data_query(start_date, end_date, day_types, periods, minutes,
                                                                     stages, transport_modes, origin_zones,
                                                                     destination_zones)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                queries = es_helper.get_from_to_map_data(start_date, end_date, day_types, periods, minutes, stages,
                                                         transport_modes, origin_zones, destination_zones)
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
        # this trips ignore metro and metrotren
        trips = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
        result = es_query.execute()
        for first in result.aggregations.strategies_without_metro_or_metrotren.first.buckets:
            for second in first.second.buckets:
                for third in second.third.buckets:
                    for fourth in third.fourth.buckets:
                        trips[first.key][second.key][third.key][fourth.key] += fourth.expansion_factor.value

        agg_names = dir(result.aggregations)
        del agg_names[agg_names.index('expansion_factor')]
        del agg_names[agg_names.index('strategies_without_metro_or_metrotren')]

        def group_strategy(item, previous_part, current_agg_name):
            if hasattr(item, 'buckets'):
                nested_strategies = []
                for bucket in item.buckets:
                    cloned_list = list(previous_part)
                    if current_agg_name.startswith('end'):
                        cloned_list[-1] = '{0} - {1}'.format(cloned_list[-1], bucket.key)
                    else:
                        cloned_list.append(bucket.key)
                    if hasattr(bucket, 'expansion_factor'):
                        cloned_list.append(bucket.expansion_factor.value)
                        nested_strategies.append(cloned_list)
                    else:
                        del bucket.doc_count
                        del bucket.key
                        next_agg_name = dir(bucket)[0]
                        nested_strategies += group_strategy(bucket[next_agg_name], cloned_list, next_agg_name)
                return nested_strategies
            else:
                if hasattr(item, 'doc_count'):
                    del item.doc_count
                next_agg_name = dir(item)[0]
                return group_strategy(item[next_agg_name], previous_part, next_agg_name)

        for agg_name in agg_names:
            strategies = group_strategy(result.aggregations[agg_name], [], agg_name)
            for strategy in strategies:
                trips[strategy[0]][strategy[1]][strategy[2]][strategy[3]] += strategy[4]
                print(strategy)
            break

        return {
            'debug': result.to_dict(),
            'strategies': trips,
            'expansionFactor': result.aggregations.expansion_factor.value,
            'docCount': result.hits.total
        }

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_types = params.getlist('daytypes[]', [])
        periods = params.getlist('period[]', [])
        minutes = params.getlist('halfHour[]', [])
        origin_zones = params.getlist('originZones[]', [])
        destination_zones = params.getlist('destinationZones[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            if export_data:
                es_query = es_helper.get_base_strategies_data_query(start_date, end_date, day_types, periods, minutes,
                                                                    origin_zones, destination_zones)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_helper.get_strategies_data(start_date, end_date, day_types, periods, minutes,
                                                         origin_zones, destination_zones)
                response.update(self.process_data(es_query))
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
                    answer[to_bucket.key][from_bucket.key] += to_bucket.doc_count

        for step in [result.first_transfer_is_end, result.second_transfer_is_end, result.third_transfer_is_end]:
            for from_bucket in step.route_from.buckets:
                for to_bucket in from_bucket.route_to.buckets:
                    end = to_bucket.key
                    if end == '-':
                        end = 'end'
                    answer[end][from_bucket.key] += to_bucket.doc_count

        for from_bucket in result.fourth_transfer_is_end.route_from.buckets:
            answer['end'][from_bucket.key] += from_bucket.doc_count

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

        es_trip_helper = ESTripHelper()
        es_stop_helper = ESStopHelper()

        try:
            if export_data:
                es_query = es_trip_helper.get_base_transfers_data_query(start_date, end_date, auth_stop_code, day_types,
                                                                        periods, half_hours)
                ExporterManager(es_query).export_data(csv_helper.TRIP_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                es_query = es_trip_helper.get_transfers_data(start_date, end_date, auth_stop_code, day_types, periods,
                                                             half_hours)[:0]
                response.update(self.process_data(es_query))
                response['stopInfo'] = es_stop_helper.get_stop_info(start_date, auth_stop_code)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
