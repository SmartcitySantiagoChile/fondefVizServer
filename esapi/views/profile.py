# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse

from esapi.helper.profile import ESProfileHelper
from esapi.helper.stop import ESStopHelper
from esapi.errors import ESQueryResultEmpty, ESQueryStopPatternTooShort, FondefVizError
from esapi.utils import check_operation_program
from esapi.messages import ExporterDataHasBeenEnqueuedMessage

from localinfo.helper import PermissionBuilder, get_day_type_list_for_select_input, get_timeperiod_list_for_select_input

from datamanager.helper import ExporterManager

from collections import defaultdict

import rqworkers.dataDownloader.csvhelper.helper as csv_helper


class MatchedStopData(View):
    """ it gives a stop list with stops that match with patter given by user """

    def get(self, request):

        term = request.GET.get("term", '')

        response = {
            'items': []
        }
        try:
            if len(term) < 3:
                raise ESQueryStopPatternTooShort()

            es_helper = ESProfileHelper()
            results = es_helper.get_matched_stop_list(term)

            for _, result in results.iteritems():
                result_list = []
                for tag in result:
                    result_list.append({"id": tag, "text": tag})

                response["items"] += result_list
        except ESQueryStopPatternTooShort as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class LoadProfileByStopData(View):
    """ It gives load profile for each bus in a stop given """

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value < 0) else value

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
        stop_code = params.get('stopCode', '')
        period = params.getlist('period[]', [])
        half_hour = params.getlist('halfHour[]', [])

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        try:
            check_operation_program(start_date, end_date)
            es_helper = ESProfileHelper()

            es_query = es_helper.get_profile_by_stop_data(start_date, end_date, day_type, stop_code, period, half_hour,
                                                          valid_operator_list)
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
        return self.process_request(request, request.POST)


class AvailableDays(View):

    def get(self, request):
        es_helper = ESProfileHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.get_available_days(valid_operator_list)

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):

        response = {}
        try:
            es_helper = ESProfileHelper()
            valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
            available_days, op_dict = es_helper.get_available_routes(valid_operator_list)

            response['availableRoutes'] = available_days
            response['operatorDict'] = op_dict
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)


class LoadProfileByExpeditionData(View):

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value < 0) else value

    def transform_answer(self, es_query):
        """ transform ES answer to something util to web client """
        trips = defaultdict(lambda: {'info': {}, 'stops': []})

        day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        time_period_dict = get_timeperiod_list_for_select_input(to_dict=True)

        for hit in es_query.scan():
            expedition_id = '{0}-{1}'.format(hit.path, hit.expeditionDayId)

            trips[expedition_id]['info'] = {
                'capacity': hit.busCapacity,
                'licensePlate': hit.licensePlate,
                'route': hit.route,
                'authTimePeriod': time_period_dict[hit.timePeriodInStartTime],
                'timeTripInit': hit.expeditionStartTime.replace('T', ' ').replace('.000Z', ''),
                'timeTripEnd': hit.expeditionEndTime.replace('T', ' ').replace('.000Z', ''),
                'dayType': day_type_dict[hit.dayType]
            }

            stop = {
                'order': hit.expeditionStopOrder,
                'name': hit.userStopName,
                'authStopCode': hit.authStopCode,
                'userStopCode': hit.userStopCode,
                'busStation': hit.busStation == 1,
                'authTimePeriod': time_period_dict[hit.timePeriodInStopTime] if hit.timePeriodInStopTime > -1 else None,
                'distOnPath': hit.stopDistanceFromPathStart,
                'stopTime': "" if hit.expeditionStopTime == "0" else hit.expeditionStopTime,
                # to avoid movement of distribution chart
                'loadProfile': self.clean_data(hit.loadProfile),
                'expandedGetIn': self.clean_data(hit.expandedBoarding),
                'expandedGetOut': self.clean_data(hit.expandedAlighting),
            }
            trips[expedition_id]['stops'].append(stop)

        for expedition_id in trips:
            trips[expedition_id]['stops'] = sorted(trips[expedition_id]['stops'], key=lambda record: record['order'])

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips

    def process_request(self, request, params, export_data=False):
        start_date = params.get('startDate', '')[:10]
        end_date = params.get('endDate', '')[:10]
        auth_route_code = params.get('authRoute')
        day_type = params.getlist('dayType[]')
        period = params.getlist('period[]')
        half_hour = params.getlist('halfHour[]')

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'trips': {}
        }

        try:
            check_operation_program(start_date, end_date)
            es_stop_helper = ESStopHelper()
            es_profile_helper = ESProfileHelper()

            es_query = es_profile_helper.get_profile_by_expedition_data(start_date, end_date, day_type, auth_route_code,
                                                                        period, half_hour, valid_operator_list)
            if export_data:
                ExporterManager(es_query).export_data(csv_helper.PROFILE_BY_EXPEDITION_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response['trips'] = self.transform_answer(es_query)
                response['stops'] = es_stop_helper.get_stop_list(auth_route_code, start_date, end_date)['stops']
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
