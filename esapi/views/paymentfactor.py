# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import rqworkers.dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import FondefVizError, ESQueryResultEmpty
from esapi.helper.paymentfactor import ESPaymentFactorHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from localinfo.helper import get_operator_list_for_select_input, get_day_type_list_for_select_input


class PaymentFactorData(View):
    """ It gives bus station distribution data """
    permission_required = 'localinfo.validation'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PaymentFactorData, self).dispatch(request, *args, **kwargs)

    def transform_es_answer(self, es_query_list, dates):
        """ transform ES answer to something useful to web client """
        result = {}
        count = 0
        for es_query in es_query_list:
            rows = []
            operator_dict = get_operator_list_for_select_input(to_dict=True)
            day_type_dict = get_day_type_list_for_select_input(to_dict=True)

            start_date = int((timezone.datetime.strptime(dates[count][0], '%Y-%m-%d') -
                              timezone.datetime(1970, 1, 1)).total_seconds() * 1000)
            end_date = int((timezone.datetime.strptime(dates[count][len(dates[count]) - 1], '%Y-%m-%d') -
                            timezone.datetime(1970, 1, 1)).total_seconds() * 1000)

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
                                date_list = sorted(e.by_date, key=lambda x: x['key'])

                                day_in_millis = 86400000
                                aux_date = start_date
                                for date in date_list:
                                    while date.key > aux_date:
                                        factor_by_date.append((aux_date, None))
                                        aux_date = aux_date + day_in_millis

                                    factor_by_date.append((date.key, date.factor.value * 100))
                                    factor_average += date.factor.value
                                    aux_date = aux_date + day_in_millis
                                factor_average = factor_average * 100 / len(date_list)

                                # complete days with empty date until end_date
                                while aux_date <= end_date:
                                    factor_by_date.append((aux_date, None))
                                    aux_date = aux_date + day_in_millis

                                # bus_station_id, bus_station_name, assignation, operator, day_type
                                row = dict(bus_station_id=a.key, bus_station_name=b.key, assignation=c.key,
                                           operator=operator_dict[d.key], operator_id=d.key, day_type=day_type_dict[e.key],
                                           total=total_value, sum=sum_value, subtraction=subtraction_value,
                                           neutral=neutral_value, factor_by_date=factor_by_date,
                                           factor_average=factor_average)
                                rows.append(row)
            count += 1
            if len(rows) == 0:
                raise ESQueryResultEmpty()

            result = {
                'rows': rows,
            }

        return result

    def process_request(self, request, params, export_data=False):
        response = {}

        dates_raw = list(request.GET.items())
        index = 0
        for indexes in range(len(dates_raw)):
            if dates_raw[indexes][0] == "dates":
                index = indexes
        dates_raw = json.loads(dates_raw[index][1])
        dates_aux = []
        dates = []
        for i in dates_raw:
            for j in i:
                dates_aux.append(str(j[0]))
            dates.append(dates_aux)
            dates_aux = []
        day_type = params.getlist('dayType[]', [])


        try:
            es_helper = ESPaymentFactorHelper()

            es_query_list = es_helper.get_data(dates, day_type)
            if export_data:
                print 'export'
                ExporterManager(es_query_list[0]).export_data(csv_helper.PAYMENT_FACTOR_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                print'no export'
                response = self.transform_es_answer(es_query_list, dates)
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
        es_helper = ESPaymentFactorHelper()
        available_days = es_helper.get_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)
