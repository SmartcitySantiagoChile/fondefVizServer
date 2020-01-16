# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from esapi.helper.profile import ESProfileHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.shape import ESShapeHelper
from esapi.errors import ESQueryResultEmpty, FondefVizError
from esapi.utils import check_operation_program
from esapi.messages import ExporterDataHasBeenEnqueuedMessage, ExpeditionsHaveBeenGroupedMessage, \
    ThereAreNotValidExpeditionsMessage
from localinfo.helper import PermissionBuilder, get_day_type_list_for_select_input, get_timeperiod_list_for_select_input
from datamanager.helper import ExporterManager
from esapi.utils import get_dates_from_request

from collections import defaultdict
from datetime import datetime

import rqworkers.dataDownloader.csvhelper.helper as csv_helper


class LoadProfileByStopData(View):
    """ It gives load profile for each bus in a stop given """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadProfileByStopData, self).dispatch(request, *args, **kwargs)

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

        dates = get_dates_from_request(request, 'GET')
        day_type = params.getlist('dayType[]', [])
        stop_code = params.get('stopCode', '')
        period = params.getlist('period[]', [])
        half_hour = params.getlist('halfHour[]', [])

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        try:
            for data_range in dates:
                check_operation_program(data_range[0], data_range[len(data_range) - 1])
            es_helper = ESProfileHelper()

            es_query = es_helper.get_profile_by_stop_data(dates, day_type, stop_code, period, half_hour,
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
        return self.process_request(request, request.POST, export_data=True)


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

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadProfileByExpeditionData, self).dispatch(request, *args, **kwargs)

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value < 0) else value

    def transform_answer(self, es_query):
        """ transform ES answer to something util to web client """
        trips = defaultdict(lambda: {'info': [], 'stops': {}})
        bus_stations = []
        expedition_not_valid_number = 0

        day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        time_period_dict = get_timeperiod_list_for_select_input(to_dict=True)

        for hit in es_query.scan():
            expedition_id = '{0}-{1}'.format(hit.path, hit.expeditionDayId)

            if len(trips[expedition_id]['info']) == 0:
                trips[expedition_id]['info'] = [
                    hit.busCapacity,
                    hit.licensePlate,
                    hit.route,
                    time_period_dict[hit.timePeriodInStartTime],
                    hit.expeditionStartTime.replace('T', ' ').replace('.000Z', ''),
                    hit.expeditionEndTime.replace('T', ' ').replace('.000Z', ''),
                    day_type_dict[hit.dayType],
                    not bool(hit.notValid)
                ]
                if bool(hit.notValid):
                    expedition_not_valid_number += 1

            if hit.busStation == 1 and hit.authStopCode not in bus_stations:
                bus_stations.append(hit.authStopCode)

            # loadProfile, expandedGetIn, expandedGetOut
            stop = [
                self.clean_data(hit.loadProfile),
                self.clean_data(hit.expandedBoarding),
                self.clean_data(hit.expandedAlighting),
            ]
            trips[expedition_id]['stops'][hit.authStopCode] = stop

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips, bus_stations, expedition_not_valid_number

    def process_request(self, request, params, export_data=False):
        dates = get_dates_from_request(request, 'GET')
        auth_route_code = params.get('authRoute')
        day_type = params.getlist('dayType[]')
        period = params.getlist('period[]')
        half_hour = params.getlist('halfHour[]')

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {}

        try:
            for date_range in dates:
                start_date = date_range[0]
                end_date = date_range[len(date_range) - 1]
                check_operation_program(start_date, end_date)
            es_stop_helper = ESStopByRouteHelper()
            es_shape_helper = ESShapeHelper()
            es_profile_helper = ESProfileHelper()

            if export_data:
                es_query = es_profile_helper.get_base_profile_by_expedition_data_query(dates, day_type,
                                                                                       auth_route_code, period,
                                                                                       half_hour, valid_operator_list)
                ExporterManager(es_query).export_data(csv_helper.PROFILE_BY_EXPEDITION_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                diff_days_length = 0
                for date_range in dates:
                    diff_days = es_profile_helper.get_available_days_between_dates(date_range[0], date_range[len(date_range) - 1],
                                                                               valid_operator_list)
                    if len(diff_days) > diff_days_length:
                        diff_days_length = len(diff_days)
                day_limit = 7

                if diff_days_length <= day_limit:
                    es_query = es_profile_helper.get_base_profile_by_expedition_data_query(dates,
                                                                                           day_type, auth_route_code,
                                                                                           period, half_hour,
                                                                                           valid_operator_list, False)
                    print("pasa query")
                    response['trips'], response['busStations'], exp_not_valid_number = self.transform_answer(es_query)
                    print("pasa trips y bus station")
                    if exp_not_valid_number:
                        response['status'] = ThereAreNotValidExpeditionsMessage(exp_not_valid_number,
                                                                                len(response['trips'].keys())). \
                            get_status_response()
                else:
                    es_query = es_profile_helper.get_profile_by_expedition_data(dates, day_type,
                                                                                auth_route_code, period, half_hour,
                                                                                valid_operator_list)
                    response['groupedTrips'] = es_query.execute().to_dict()
                    response['status'] = ExpeditionsHaveBeenGroupedMessage(day_limit).get_status_response()
                response['stops'] = []
                response['shape'] = []
                response['stops'].append(es_stop_helper.get_stop_list(auth_route_code, dates)['stops'])
                response['shape'] = es_shape_helper.get_route_shape(auth_route_code, dates)['points']

        except FondefVizError as e:
            response['status'] = e.get_status_response()
        print("termino")
        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)


class LoadProfileByTrajectoryData(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoadProfileByTrajectoryData, self).dispatch(request, *args, **kwargs)

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value < 0) else value

    def transform_answer(self, es_query):
        """ transform ES answer to something util to web client """
        trips = defaultdict(lambda: {'info': {}, 'stops': {}})
        bus_stations = []
        expedition_not_valid_number = 0

        day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        time_period_dict = get_timeperiod_list_for_select_input(to_dict=True)
        # TODO: replace random value with value given by data
        import random
        for hit in es_query.scan():
            expedition_id = '{0}-{1}'.format(hit.path, hit.expeditionDayId)

            if 'capacity' not in trips[expedition_id]['info']:
                is_valid = int(round(random.uniform(0, 1)))
                trips[expedition_id]['info'] = {
                    'capacity': hit.busCapacity,
                    'licensePlate': hit.licensePlate,
                    'route': hit.route,
                    'authTimePeriod': time_period_dict[hit.timePeriodInStartTime],
                    'timeTripInit': hit.expeditionStartTime.replace('T', ' ').replace('.000Z', ''),
                    'timeTripEnd': hit.expeditionEndTime.replace('T', ' ').replace('.000Z', ''),
                    'dayType': day_type_dict[hit.dayType],
                    'valid': bool(is_valid)
                }
                if not is_valid:
                    expedition_not_valid_number += 1

            if hit.busStation == 1 and hit.authStopCode not in bus_stations:
                bus_stations.append(hit.authStopCode)

            stop = [
                hit.stopDistanceFromPathStart,
                self.clean_data(hit.loadProfile),
                self.clean_data(hit.expandedBoarding),
                self.clean_data(hit.expandedAlighting),
                hit.expeditionStopTime
            ]
            trips[expedition_id]['stops'][hit.authStopCode] = stop

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips, bus_stations, expedition_not_valid_number

    def process_request(self, request, params, export_data=False):

        dates = get_dates_from_request(request, 'GET')
        auth_route_code = params.get('authRoute')
        day_type = params.getlist('dayType[]')
        period = params.getlist('period[]')
        half_hour = params.getlist('halfHour[]')

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {}

        try:
            for date_range in dates:
                start_date = date_range[0]
                end_date = date_range[len(date_range) - 1]
                check_operation_program(start_date, end_date)
            es_stop_helper = ESStopByRouteHelper()
            es_profile_helper = ESProfileHelper()

            es_query = es_profile_helper.get_base_profile_by_trajectory_data_query(dates, day_type,
                                                                                   auth_route_code, period, half_hour,
                                                                                   valid_operator_list)
            if export_data:
                ExporterManager(es_query).export_data(csv_helper.PROFILE_BY_EXPEDITION_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response['trips'], response['busStations'], exp_not_valid_number = self.transform_answer(es_query)
                response['stops'] = es_stop_helper.get_stop_list(auth_route_code, dates)['stops']
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
