# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import rqworkers.dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import FondefVizError, ESQueryResultEmpty
from esapi.helper.busstationdistribution import ESBusStationDistributionHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from localinfo.helper import get_operator_list_for_select_input, get_day_type_list_for_select_input


class BusStationDistributionData(View):
    """ It gives bus station distribution data """
    permission_required = 'localinfo.validation'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BusStationDistributionData, self).dispatch(request, *args, **kwargs)

    def transform_es_answer(self, es_query):
        """ transform ES answer to something util to web client """
        rows = []

        operator_dict = get_operator_list_for_select_input(to_dict=True)
        day_type_dict = get_day_type_list_for_select_input(to_dict=True)

        for a in es_query.execute().aggregations.by_bus_station_id.buckets:
            for b in a.by_bus_station_name.buckets:
                for c in b.by_assignation.buckets:
                    for d in c.by_operator.buckets:
                        for e in d.by_day_type.buckets:
                            total_value = e.total.value
                            sum_value = e.sum.value
                            subtraction_value = e.subtraction.value
                            neutral_value = e.neutral.value

                            factor_by_date = []
                            factor_average = 0
                            for date in e.by_date:
                                factor_by_date.append((date.key, date.factor.value * 100))
                                factor_average += date.factor.value
                            factor_average = factor_average * 100 / len(factor_by_date)

                            # bus_station_id, bus_station_name, assignation, operator, day_type
                            row = dict(bus_station_id=a.key, bus_station_name=b.key, assignation=c.key,
                                       operator=operator_dict[d.key], operator_id=d.key, day_type=day_type_dict[e.key],
                                       total=total_value, sum=sum_value, subtraction=subtraction_value,
                                       neutral=neutral_value, factor_by_date=factor_by_date,
                                       factor_average=factor_average)
                            rows.append(row)

        if len(rows) == 0:
            raise ESQueryResultEmpty()

        result = {
            'rows': rows,
        }

        return result

    def process_request(self, request, params, export_data=False):
        response = {}

        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_type = params.getlist('dayType[]', [])
        exclude_dates = list(map(lambda x: x[:10], params.getlist('excludeDates[]', [])))

        try:
            es_helper = ESBusStationDistributionHelper()

            es_query = es_helper.get_data(start_date, end_date, day_type, exclude_dates)
            if export_data:
                ExporterManager(es_query).export_data(csv_helper.BUS_STATION_DISTRIBUTION_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response = self.transform_es_answer(es_query)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class AvailableDays(View):
    permission_required = 'localinfo.validation'

    def get(self, request):
        es_helper = ESBusStationDistributionHelper()
        available_days = es_helper.get_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)
