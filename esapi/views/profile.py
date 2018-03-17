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
            results = es_helper.ask_for_stop(term)

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
            data = hit.to_dict()

            if len(info.keys()) == 0:
                info['authorityStopCode'] = data['authStopCode']
                info['userStopCode'] = data['userStopCode']
                info['name'] = data['userStopName']
                info['busStation'] = data['busStation'] == "1"

            expedition_id = '{0}-{1}'.format(data['path'], data['expeditionDayId'])

            trips[expedition_id] = {
                'capacity': data['busCapacity'],
                'licensePlate': data['licensePlate'],
                'route': data['route'],
                'stopTime': "" if data['expeditionStopTime'] == "0" else data['expeditionStopTime'],
                'stopTimePeriod': time_period_dict[data['timePeriodInStopTime']],
                'dayType': day_type_dict[data['dayType']],
                'distOnPath': data['stopDistanceFromPathStart'],
                # to avoid movement of distribution chart
                'loadProfile': self.clean_data(data['loadProfile']),
                'expandedGetIn': self.clean_data(data['expandedBoarding']),
                'expandedLanding': self.clean_data(data['expandedAlighting'])
            }

        if len(info.keys()) == 0:
            raise ESQueryResultEmpty()

        result = {
            'info': info,
            'trips': trips
        }

        return result

    def get(self, request):
        """ expedition data """
        response = {}

        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        day_type = request.GET.getlist('dayType[]', [])
        stop_code = request.GET.get('stopCode', '')
        period = request.GET.getlist('period[]', [])
        half_hour = request.GET.getlist('halfHour[]', [])
        export_data = True if request.GET.get('exportData', False) == 'true' else False

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        try:
            check_operation_program(start_date, end_date)
            es_helper = ESProfileHelper()

            es_query = es_helper.ask_for_profile_by_stop(start_date, end_date, day_type, stop_code, period, half_hour,
                                                         valid_operator_list).scan()
            if export_data:
                ExporterManager(es_query).export_data()
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response = self.transform_es_answer(es_query)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class AvailableDays(View):

    def get(self, request):
        es_helper = ESProfileHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.ask_for_available_days(valid_operator_list)

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
            available_days, op_dict = es_helper.ask_for_available_routes(valid_operator_list)

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
            data = hit.to_dict()
            expedition_id = '{0}-{1}'.format(data['path'], data['expeditionDayId'])

            trips[expedition_id]['info'] = {
                'capacity': data['busCapacity'],
                'licensePlate': data['licensePlate'],
                'route': data['route'],
                'authTimePeriod': time_period_dict[data['timePeriodInStartTime']],
                'timeTripInit': data['expeditionStartTime'].replace('T', ' ').replace('.000Z', ''),
                'timeTripEnd': data['expeditionEndTime'].replace('T', ' ').replace('.000Z', ''),
                'dayType': day_type_dict[data['dayType']]
            }

            stop = {
                'order': data['expeditionStopOrder'],
                'name': data['userStopName'],
                'authStopCode': data['authStopCode'],
                'userStopCode': data['userStopCode'],
                'busStation': data['busStation'] == "1",
                'authTimePeriod': time_period_dict[data['timePeriodInStopTime']],
                'distOnPath': data['stopDistanceFromPathStart'],
                'stopTime': "" if data['expeditionStopTime'] == "0" else data['expeditionStopTime'],
                # to avoid movement of distribution chart
                'loadProfile': self.clean_data(data['loadProfile']),
                'expandedGetIn': self.clean_data(data['expandedBoarding']),
                'expandedGetOut': self.clean_data(data['expandedAlighting']),
            }
            trips[expedition_id]['stops'].append(stop)

        for expedition_id in trips:
            trips[expedition_id]['stops'] = sorted(trips[expedition_id]['stops'], key=lambda record: record['order'])

        if len(trips.keys()) == 0:
            raise ESQueryResultEmpty()

        return trips

    def get(self, request):
        """ expedition data """

        start_date = request.GET.get('startDate', '')[:10]
        end_date = request.GET.get('endDate', '')[:10]
        auth_route_code = request.GET.get('authRoute')
        day_type = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        half_hour = request.GET.getlist('halfHour[]')
        export_data = True if request.GET.get('exportData', False) == 'true' else False

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)

        response = {
            'trips': {}
        }

        try:
            check_operation_program(start_date, end_date)
            es_stop_helper = ESStopHelper()
            es_profile_helper = ESProfileHelper()

            es_query = es_profile_helper.ask_for_profile_by_expedition(start_date, end_date, day_type, auth_route_code,
                                                                       period, half_hour, valid_operator_list)
            if export_data:
                ExporterManager(es_query).export_data()
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                response['trips'] = self.transform_answer(es_query)
                response['stops'] = es_stop_helper.get_stop_list(auth_route_code, start_date, end_date)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)
