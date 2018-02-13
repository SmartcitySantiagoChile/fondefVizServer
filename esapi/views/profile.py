# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse

from esapi.helper.profile import ESProfileHelper
from esapi.errors import ESQueryResultEmpty, ESQueryStopParameterDoesNotExist, ESQueryStopPatternTooShort, \
    ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist


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
        return 0 if (-1 < value and value < 0) else value

    def transform_es_answer(self, result_iterator):
        """ transform ES answer to something util to web client """
        info = {}
        trips = {}

        for hit in result_iterator:
            data = hit.to_dict()

            if len(info.keys()) == 0:
                info['authorityStopCode'] = data['authStopCode']
                info['userStopCode'] = data['userStopCode']
                info['name'] = data['userStopName']
                info['busStation'] = data['busStation'] == "1"

            expedition_id = data['expeditionDayId']

            trips[expedition_id] = {}
            trips[expedition_id]['capacity'] = int(data['busCapacity'])
            trips[expedition_id]['licensePlate'] = data['licensePlate']
            trips[expedition_id]['route'] = data['route']
            trips[expedition_id]['stopTime'] = "" if data['expeditionStopTime'] == "0" else \
                data['expeditionStopTime'].replace('T', ' ').replace('.000Z', '')
            trips[expedition_id]['stopTimePeriod'] = data['timePeriodInStopTime']
            trips[expedition_id]['dayType'] = data['dayType']
            trips[expedition_id]['distOnPath'] = data['stopDistanceFromPathStart']

            # to avoid movement of distribution chart
            trips[expedition_id]['loadProfile'] = self.clean_data(data['loadProfile'])
            trips[expedition_id]['expandedGetIn'] = self.clean_data(data['expandedBoarding'])
            trips[expedition_id]['expandedLanding'] = self.clean_data(data['expandedAlighting'])

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

        try:
            es_helper = ESProfileHelper()
            result_iterator = es_helper.ask_for_profile_by_stop(start_date, end_date, day_type, stop_code, period,
                                                                half_hour).scan()
            response = self.transform_es_answer(result_iterator)
            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryStopParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class AvailableDays(View):

    def get(self, request):
        es_helper = ESProfileHelper()
        available_days = es_helper.ask_for_available_days()

        response = {}
        response['availableDays'] = available_days

        return JsonResponse(response)


class AvailableRoutes(View):

    def get(self, request):
        es_helper = ESProfileHelper()
        available_days, op_dict = es_helper.ask_for_available_routes()

        response = {}
        response['availableRoutes'] = available_days
        response['operatorDict'] = op_dict

        return JsonResponse(response)


class LoadProfileByExpeditionData(View):

    def clean_data(self, data):
        """ round to zero values between [-1, 0]"""
        value = float(data)
        return 0 if (-1 < value and value < 0) else value

    def transform_answer(self, result_iterator):
        """ transform ES answer to something util to web client """
        trips = {}

        for hit in result_iterator:
            data = hit.to_dict()

            expedition_id = data['expeditionDayId']
            if expedition_id not in trips:
                trips[expedition_id] = {'info': {}, 'stops': []}

            trips[expedition_id]['info']['capacity'] = int(data['busCapacity'])
            trips[expedition_id]['info']['licensePlate'] = data['licensePlate']
            trips[expedition_id]['info']['route'] = data['route']
            trips[expedition_id]['info']['authTimePeriod'] = data['timePeriodInStartTime']
            trips[expedition_id]['info']['timeTripInit'] = data['expeditionStartTime'].replace('T', ' ').replace(
                '.000Z',
                '')
            trips[expedition_id]['info']['timeTripEnd'] = data['expeditionEndTime'].replace('T', ' ').replace('.000Z',
                                                                                                              '')
            trips[expedition_id]['info']['dayType'] = data['dayType']

            stop = {}
            stop['name'] = data['userStopName']
            stop['authStopCode'] = data['authStopCode']
            stop['userStopCode'] = data['userStopCode']
            stop['busStation'] = data['busStation'] == "1"
            stop['authTimePeriod'] = data['timePeriodInStopTime']
            stop['distOnPath'] = data['stopDistanceFromPathStart']
            stop['stopTime'] = "" if data['expeditionStopTime'] == "0" else \
                data['expeditionStopTime'].replace('T', ' ').replace('.000Z', '')
            stop['order'] = int(data['expeditionStopOrder'])

            # to avoid movement of distribution chart
            stop['loadProfile'] = self.clean_data(data['loadProfile'])
            stop['expandedGetIn'] = self.clean_data(data['expandedBoarding'])
            stop['expandedGetOut'] = self.clean_data(data['expandedAlighting'])
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
        route = request.GET.get('authRoute')
        day_type = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        half_hour = request.GET.getlist('halfHour[]')

        # license_plate = request.GET.getlist('licensePlate[]')
        # expedition_id = request.GET.getlist('expeditionId[]')

        es_helper = ESProfileHelper()

        response = {
            'trips': {}
        }

        try:
            result_iterator = es_helper.ask_for_profile_by_expedition(start_date, end_date, day_type, route, period,
                                                                      half_hour).scan()
            response['trips'] = self.transform_answer(result_iterator)
            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)
