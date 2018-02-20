# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from esapi.helper.trip import ESTripHelper
from esapi.errors import ESQueryResultEmpty, ESQueryParametersDoesNotExist, ESQueryDateRangeParametersDoesNotExist


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
        day_types = request.GET.getlist('daytypes[]', [])
        periods = request.GET.getlist('periods[]', [])
        origin_zones = int(request.GET.getlist('origin[]', []))
        destination_zones = int(request.GET.getlist('destination[]', []))

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
        day_types = request.GET.getlist('daytypes[]', [])
        periods = request.GET.getlist('periods[]', [])

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
