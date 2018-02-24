# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from collections import defaultdict

from esapi.helper.trip import ESTripHelper
from esapi.errors import ESQueryResultEmpty, ESQueryParametersDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryStagesEmpty, ESQueryOriginZoneParameterDoesNotExist, ESQueryDestinationZoneParameterDoesNotExist


class ResumeData(View):

    def process_data(self, data_dict):

        return data_dict

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.
        """
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_types = request.GET.getlist('dayType[]', [])
        periods = request.GET.getlist('period[]', [])
        origin_zones = map(lambda x: int(x), request.GET.getlist('origin[]', []))
        destination_zones = map(lambda x: int(x), request.GET.getlist('destination[]', []))

        es_helper = ESTripHelper()

        response = {}

        try:
            es_query_dict = es_helper.ask_for_resume_data(start_date, end_date, day_types, periods, origin_zones,
                                                          destination_zones)
            response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class MapData(View):

    def process_data(self, data_dict):

        return data_dict

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.
        """
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_types = request.GET.getlist('dayType[]', [])
        periods = request.GET.getlist('boardingPeriod[]', [])

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
            es_query_dict = es_helper.ask_for_map_data(start_date, end_date, day_types, periods, sectors)
            response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class AvailableDays(View):

    def get(self, request):
        es_helper = ESTripHelper()
        available_days = es_helper.ask_for_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class LargeTravelData(View):

    def process_data(self, data):
        return data

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.

        The response is a Json document.
        """
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_types = request.GET.getlist('dayType[]', [])
        periods = request.GET.getlist('period[]', [])
        stages = request.GET.getlist('stages[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            es_query_dict = es_helper.ask_for_large_travel_data(start_date, end_date, day_types, periods, stages)
            response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty,
                ESQueryStagesEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class FromToMapData(View):

    def process_data(self, data):
        return data

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.

        The response is a Json document.
        """
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_types = request.GET.getlist('dayType[]', [])
        periods = request.GET.getlist('period[]', [])
        minutes = request.GET.getlist('halfHour[]', [])
        stages = request.GET.getlist('stages[]', [])
        modes = request.GET.getlist('modes[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            es_query_dict = es_helper.ask_for_from_to_map_data(start_date, end_date, day_types, periods, minutes,
                                                               stages, modes)
            response.update(self.process_data(es_helper.make_multisearch_query_for_aggs(es_query_dict)))
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty,
                ESQueryStagesEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class StrategiesData(View):

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

    def get(self, request):
        """
        It returns travel data based on the requested filters.
        The data is optimized for by_time views.

        The response is a Json document.
        """
        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_types = request.GET.getlist('daytypes[]', [])
        periods = request.GET.getlist('period[]', [])
        minutes = request.GET.getlist('halfHour[]', [])
        origin_zone = request.GET.getlist('origins[]', [])
        destination_zone = request.GET.getlist('destinations[]', [])

        response = {}

        es_helper = ESTripHelper()

        try:
            es_query = es_helper.ask_for_strategies_data(start_date, end_date, day_types, periods, minutes,
                                                         origin_zone, destination_zone)
            response['strategies'] = self.process_data(es_query)
        except (ESQueryDateRangeParametersDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty,
                ESQueryStagesEmpty, ESQueryOriginZoneParameterDoesNotExist,
                ESQueryDestinationZoneParameterDoesNotExist) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)
