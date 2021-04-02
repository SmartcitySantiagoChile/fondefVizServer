# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from unittest import mock
from django.urls import reverse

from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryOperatorParameterDoesNotExist, \
    ESQueryStopParameterDoesNotExist, ESQueryResultEmpty, ESQueryDateParametersDoesNotExist, FondefVizError
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class LoadProfileByStopTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:loadProfileByStopData')
        self.data = {
            'dates': '[[""]]',
            'stopCode': '',
            'dayType[]': [],
            'period': [],
            'halfHour': []
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['stopCode'] = 'PA433'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_with_result(self, check_operation_program, es_query):
        check_operation_program.return_value = None
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        hit = mock.Mock()
        type(hit).timePeriodInStopTime = mock.PropertyMock(return_value=9)
        type(hit).dayType = mock.PropertyMock(return_value=0)
        type(hit).loadProfile = mock.PropertyMock(return_value=36.33063507)
        type(hit).expandedBoarding = mock.PropertyMock(return_value=1.215768337)
        type(hit).expandedAlighting = mock.PropertyMock(return_value=1.073773265)
        type(hit).userStopCode = mock.PropertyMock(return_value='PJ2')
        type(hit).authStopCode = mock.PropertyMock(return_value='T-8-65-NS-10')
        type(hit).userStopName = mock.PropertyMock(return_value='Lo Espinoza esq- / Carmen Lidia')
        type(hit).busStation = mock.PropertyMock(return_value=1)
        type(hit).licensePlate = mock.PropertyMock(return_value='ZN-6496')
        type(hit).busCapacity = mock.PropertyMock(return_value=91)
        type(hit).route = mock.PropertyMock(return_value='T101 00I')
        type(hit).stopDistanceFromPathStart = mock.PropertyMock(return_value=9663)
        type(hit).expeditionStopTime = mock.PropertyMock(return_value='2017-07-31T17:39:36.000Z')
        type(hit).expeditionDayId = mock.PropertyMock(return_value=152)
        type(hit).path = mock.PropertyMock(return_value='path')
        es_query_instance.scan.return_value = [hit]
        expected = {"info": {"userStopCode": "PJ2", "busStation": True, "authorityStopCode": "T-8-65-NS-10",
                             "name": "Lo Espinoza esq- / Carmen Lidia"}, "trips": {
            "path-152": {"licensePlate": "ZN-6496", "capacity": 91, "expandedGetIn": 1.215768337,
                         "stopTimePeriod": "Punta tarde (17:30:00-20:29:59)", "loadProfile": 36.33063507,
                         "dayType": "Laboral",
                         "route": "T101 00I", "distOnPath": 9663, "stopTime": "2017-07-31T17:39:36.000Z",
                         "expandedLanding": 1.073773265}}}

        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'stopCode': 'PA433'
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_without_result(self, check_operation_program, es_query):
        check_operation_program.return_value = None
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['stopCode'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.profile.ExporterManager')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['stopCode'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class AvailableDaysTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableProfileDays')
        self.data = {}
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days')
    def test_ask_for_days_with_data(self, get_available_days):
        get_available_days.return_value = [self.available_date]
        response = self.client.get(self.url, self.data)
        expected = {
            'availableDays': [self.available_date],
            'info': []
        }
        self.assertJSONEqual(response.content, expected)


class AvailableRoutesTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableProfileRoutes')
        self.data = {}
        self.available_route = '506 00I'

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_routes')
    def test_ask_for_routes_with_data(self, get_available_routes):
        available_days = {'Metbus': {'506': [self.available_route]}}
        get_available_routes.return_value = (available_days, [])
        response = self.client.get(self.url, self.data)
        expected = {
            'availableRoutes': {
                'Metbus': {
                    '506': [self.available_route]
                }
            },
            'operatorDict': [],
            'routesDict': {},
            'opProgramDates': {}
        }
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_routes')
    def test_ask_for_routes_without_data(self, get_available_routes):
        get_available_routes.side_effect = ESQueryOperatorParameterDoesNotExist()
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryOperatorParameterDoesNotExist().get_status_response())


class LoadProfileByExpeditionTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:loadProfileByExpeditionData')
        self.data = {
            'dates': '[[""]]',
            'authRoute': '',
            'dayType[]': [],
            'period[]': [],
            'halfHour[]': []
        }

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_wrong_route(self, check_operation_program, get_available_days_between_dates):
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryRouteParameterDoesNotExist().get_status_response())

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    def test_exec_elasticsearch_query_with_result(self, get_route_shape, get_stop_list, es_query,
                                                  check_operation_program,
                                                  get_available_days_between_dates):
        get_stop_list.return_value = {'stops': []}
        get_route_shape.return_value = {'points': []}
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance

        hit = mock.Mock()
        type(hit).timePeriodInStartTime = mock.PropertyMock(return_value=8)
        type(hit).dayType = mock.PropertyMock(return_value=0)
        type(hit).loadProfile = mock.PropertyMock(return_value=36.33063507)
        type(hit).expandedBoarding = mock.PropertyMock(return_value=1.215768337)
        type(hit).expandedAlighting = mock.PropertyMock(return_value=1.073773265)
        type(hit).authStopCode = mock.PropertyMock(return_value='T-8-65-NS-10')
        type(hit).busStation = mock.PropertyMock(return_value=1)
        type(hit).licensePlate = mock.PropertyMock(return_value='ZN-6496')
        type(hit).busCapacity = mock.PropertyMock(return_value=91)
        type(hit).route = mock.PropertyMock(return_value='T101 00I')
        type(hit).expeditionEndTime = mock.PropertyMock(return_value='2017-07-31T17:39:36.000Z')
        type(hit).expeditionStartTime = mock.PropertyMock(return_value='2017-07-31T16:59:11.000Z')
        type(hit).expeditionDayId = mock.PropertyMock(return_value=152)
        type(hit).path = mock.PropertyMock(return_value='path')
        type(hit).notValid = mock.PropertyMock(return_value=1)
        type(hit).expandedEvasionBoarding = mock.PropertyMock(return_value=0)
        type(hit).expandedEvasionAlighting = mock.PropertyMock(return_value=0)
        type(hit).expandedBoardingPlusExpandedEvasionBoarding = mock.PropertyMock(return_value=0)
        type(hit).expandedAlightingPlusExpandedEvasionAlighting = mock.PropertyMock(return_value=0)
        type(hit).loadProfileWithEvasion = mock.PropertyMock(return_value=0)
        type(hit).boardingWithAlighting = mock.PropertyMock(return_value=0)

        es_query_instance.scan.return_value = [hit]
        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'authRoute': '506 00I'
        }
        expected = {
            "message": "Hay 1 expediciones no v\u00e1lidas de 1. Para que la expedici\u00f3n no se v\u00e1lida debe cumplir alguna de las siguientes condiciones:<br /><ul><li>Porcentaje de paraderos con carga menor a -1 es superior al 1 %</li><li>Porcentaje de paraderos con carga mayor al 1 % sobre la capacidad del bus es superior al 1%</li></ul>",
            "code": 253, "type": "warning", "title": "Hay expediciones no v\u00e1lidas"}
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, expected)

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    def test_exec_elasticsearch_query_without_result(self, get_route_shape, get_stop_list, es_query,
                                                     check_operation_program,
                                                     get_available_days_between_dates):
        get_stop_list.return_value = {'stops': []}
        get_route_shape.return_value = {'points': []}
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan = mock.Mock(side_effect=ESQueryResultEmpty)
        data = {
            'dates': '[["2019-01-01"]]',
            'dayType[]': ['SABADO'],
            'period[]': [],
            'halfHour[]': [],
            'authRoute': '506 00I'
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.helper.profile.ESProfileHelper.get_profile_by_expedition_data')
    @mock.patch('esapi.views.profile.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    def test_exec_elasticsearch_query_over_day_limit(self, get_route_shape, get_stop_list, es_query, mock_method,
                                                     get_profile_by_expedition_data, get_available_days_between_dates):
        get_stop_list.return_value = {'stops': []}
        get_route_shape.return_value = {'points': []}
        get_available_days_between_dates.return_value = [None] * 8
        get_profile_by_expedition_data.return_value = get_profile_by_expedition_data
        get_profile_by_expedition_data.execute.return_value = get_profile_by_expedition_data
        get_profile_by_expedition_data.to_dict.return_value = 'groupedTrips'
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []
        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'authRoute': '506 00I'
        }
        expected = {
            "message": "El per\u00edodo seleccionado es superior a 7 d\u00edas por lo que se ha omitido la tabla de "
                       "expediciones",
            "code": 252, "type": "info", "title": "Expediciones omitidas"
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, expected)

    @mock.patch('esapi.views.profile.ExporterManager')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class LoadProfileByTrajectoryTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:loadProfileByTrajectoryData')
        self.data = {
            'dates': '[[""]]',
            'authRoute': '',
            'dayType[]': [],
            'period[]': [],
            'halfHour[]': []
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_wrong_route(self, check_operation_program, get_available_days_between_dates):
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryRouteParameterDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    def test_exec_elasticsearch_query_with_result(self, get_route_shape, get_stop_list, es_query,
                                                  check_operation_program, get_available_days_between_dates):
        get_stop_list.return_value = {'stops': []}
        get_route_shape.return_value = {'points': []}
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance

        hit = mock.Mock()
        type(hit).timePeriodInStartTime = mock.PropertyMock(return_value=8)
        type(hit).dayType = mock.PropertyMock(return_value=0)
        type(hit).loadProfile = mock.PropertyMock(return_value=36.33063507)
        type(hit).expandedBoarding = mock.PropertyMock(return_value=1.215768337)
        type(hit).expandedAlighting = mock.PropertyMock(return_value=1.073773265)
        type(hit).authStopCode = mock.PropertyMock(return_value='T-8-65-NS-10')
        type(hit).busStation = mock.PropertyMock(return_value=1)
        type(hit).licensePlate = mock.PropertyMock(return_value='ZN-6496')
        type(hit).busCapacity = mock.PropertyMock(return_value=91)
        type(hit).expeditionStopTime = mock.PropertyMock(return_value='2017-07-31T17:39:36.000Z')
        type(hit).stopDistanceFromPathStart = mock.PropertyMock(return_value=9663)
        type(hit).route = mock.PropertyMock(return_value='T101 00I')
        type(hit).expeditionEndTime = mock.PropertyMock(return_value='2017-07-31T17:39:36.000Z')
        type(hit).expeditionStartTime = mock.PropertyMock(return_value='2017-07-31T16:59:11.000Z')
        type(hit).expeditionDayId = mock.PropertyMock(return_value=152)
        type(hit).path = mock.PropertyMock(return_value='path')
        type(hit).notValid = mock.PropertyMock(return_value=0)
        es_query_instance.scan.return_value = [hit]
        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'authRoute': '506 00I'
        }
        expected = {"busStations": ["T-8-65-NS-10"], "trips": {"path-152": {
            "info": {"licensePlate": "ZN-6496", "capacity": 91, "valid": True, "timeTripInit": "2017-07-31 16:59:11",
                     "dayType": "Laboral", "route": "T101 00I",
                     "authTimePeriod": "Fuera de punta tarde (14:00:00-17:29:59)",
                     "timeTripEnd": "2017-07-31 17:39:36"},
            "stops": {"T-8-65-NS-10": [9663, 36.33063507, 1.215768337, 1.073773265, "2017-07-31T17:39:36.000Z"]}}},
                    "stops": []}
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.profile.ESProfileHelper.get_available_days_between_dates')
    @mock.patch('esapi.views.profile.check_operation_program')
    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.helper.stopbyroute.ESStopByRouteHelper.get_stop_list')
    @mock.patch('esapi.helper.shape.ESShapeHelper.get_route_shape')
    def test_exec_elasticsearch_query_without_result(self, get_route_shape, get_stop_list, es_query,
                                                     check_operation_program,
                                                     get_available_days_between_dates):
        get_stop_list.return_value = {'stops': []}
        get_route_shape.return_value = {'points': []}
        check_operation_program.return_value = None
        get_available_days_between_dates.return_value = []
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []
        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [0, 1, 2],
            'halfHour[]': [0, 1, 2],
            'authRoute': '506 00I'
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.profile.ExporterManager')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class LoadBoardingAndAlightingAverageByStopsTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:boardingAndAlightingAverageByStops')
        self.data = {
            'dates': '[[""]]',
            'stopCodes[]': [],
            'dayType[]': [],
            'period': [],
            'halfHour': []
        }

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['stopCodes[]'] = ["PA433"]
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    def test_wrong_stop_code(self):
        self.data['dates'] = '[["2018-01-01"]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryStopParameterDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.basehelper.Search')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_without_result(self, check_operation_program, es_query):
        check_operation_program.return_value = None
        es_query_instance = es_query.return_value
        es_query_instance.filter.return_value = es_query_instance
        es_query_instance.query.return_value = es_query_instance
        es_query_instance.source.return_value = es_query_instance
        es_query_instance.scan.return_value = []
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['stopCodes[]'] = ['506 00I']
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.profile.ExporterManager')
    @mock.patch('esapi.views.profile.check_operation_program')
    def test_exec_elasticsearch_query_post(self, check_operation_program, exporter_manager):
        check_operation_program.return_value = None
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        self.data['dates'] = '[["2018-01-01"]]'
        self.data['stopCodes[]'] = ['506 00I']
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())
