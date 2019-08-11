# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import rqworkers.dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import ESQueryResultEmpty, FondefVizError
from esapi.helper.busstationdistribution import ESBusStationDistributionHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from esapi.utils import check_operation_program
from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input


class BusStationDistributionData(View):
    """ It gives bus station distribution data """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BusStationDistributionData, self).dispatch(request, *args, **kwargs)

    def transform_es_answer(self, es_query):
        """ transform ES answer to something util to web client """
        info = {}
        trips = {}

        day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        time_period_dict = get_timeperiod_list_for_select_input(to_dict=True)

        for hit in es_query.scan():

            if len(info.keys()) == 0:
                info['authorityStopCode'] = hit.authStopCode
                info['userStopCode'] = hit.userStopCode
                info['name'] = hit.userStopName
                info['busStation'] = hit.busStation == 1

            expedition_id = '{0}-{1}'.format(hit.path, hit.expeditionDayId)

            trips[expedition_id] = {
                'capacity': hit.busCapacity,
                'licensePlate': hit.licensePlate,
                'route': hit.route,
                'stopTime': "" if hit.expeditionStopTime == "0" else hit.expeditionStopTime,
                'stopTimePeriod': time_period_dict[hit.timePeriodInStopTime] if hit.timePeriodInStopTime > -1 else None,
                'dayType': day_type_dict[hit.dayType],
                'distOnPath': hit.stopDistanceFromPathStart,
                # to avoid movement of distribution chart
                'loadProfile': self.clean_data(hit.loadProfile),
                'expandedGetIn': self.clean_data(hit.expandedBoarding),
                'expandedLanding': self.clean_data(hit.expandedAlighting)
            }

        if len(info.keys()) == 0:
            raise ESQueryResultEmpty()

        result = {
            'info': info,
            'trips': trips
        }

        return result

    def process_request(self, request, params, export_data=False):
        response = {}

        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        day_type = params.getlist('dayType[]', [])

        try:
            check_operation_program(start_date, end_date)
            es_helper = ESBusStationDistributionHelper()

            es_query = es_helper.get_data(start_date, end_date, day_type)
            if export_data:
                ExporterManager(es_query).export_data(csv_helper.PROFILE_BY_STOP_DATA, request.user)
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

    def get(self, request):
        es_helper = ESBusStationDistributionHelper()
        available_days = es_helper.get_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)
