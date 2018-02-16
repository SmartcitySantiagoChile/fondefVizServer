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
        origin_zone = int(request.GET.get('origin', -1))
        destination_zone = int(request.GET.get('destination', -1))

        es_helper = ESTripHelper()

        response = {}

        try:
            es_query_dict = es_helper.ask_for_resume_data(start_date, end_date, day_types, periods, origin_zone,
                                                          destination_zone)
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
