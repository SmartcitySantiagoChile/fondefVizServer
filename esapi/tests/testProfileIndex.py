from unittest import mock

from django.test import TestCase
from elasticsearch_dsl import Search

from esapi.errors import ESQueryRouteParameterDoesNotExist, ESQueryDateRangeParametersDoesNotExist, \
    ESQueryOperatorParameterDoesNotExist, ESQueryStopParameterDoesNotExist
from esapi.helper.profile import ESProfileHelper


class ESProfileIndexTest(TestCase):

    def setUp(self):
        self.instance = ESProfileHelper()

    def test_get_profile_by_stop_data(self):
        dates = [[""]]
        day_type = ['LABORAL']
        stop_code = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_profile_by_stop_data, dates,
                          day_type, stop_code, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_profile_by_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        stop_code = 'PA433'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_profile_by_stop_data(dates, day_type, stop_code, period, half_hour,
                                                        valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'term': {'fulfillment': 'C'}}, {'terms': {'operator': [1, 2, 3]}},
                                                  {'terms': {'dayType': ['LABORAL']}},
                                                  {'terms': {'timePeriodInStopTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStopTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {'gte': '2018-01-01||/d', 'lte': '2018-01-02||/d', 'format': 'yyyy-MM-dd',
                                        'time_zone': '+00:00'}}}], 'must': [{'term': {'authStopCode.raw': 'PA433'}}]}},
                    '_source': ['busCapacity', 'expeditionStopTime', 'licensePlate', 'route', 'expeditionDayId',
                                'userStopName', 'expandedAlighting', 'expandedBoarding', 'fulfillment',
                                'stopDistanceFromPathStart', 'expeditionStartTime', 'expeditionEndTime', 'authStopCode',
                                'userStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                                'loadProfile', 'busStation', 'path', 'expandedEvasionBoarding',
                                'expandedEvasionAlighting', 'expandedBoardingPlusExpandedEvasionBoarding',
                                'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
                                'boardingWithAlighting']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days(self, _get_available_days):
        _get_available_days.return_value = list()
        result = self.instance.get_available_days(valid_operator_list=[])
        self.assertListEqual(result, [])

    def test_get_available_routes_without_operator_list(self):
        self.assertRaises(ESQueryOperatorParameterDoesNotExist,
                          self.instance.get_available_routes, valid_operator_list=[])

    @mock.patch('esapi.helper.profile.get_operator_list_for_select_input')
    @mock.patch('esapi.helper.profile.ESProfileHelper.get_base_query')
    def test_get_available_routes(self, get_base_query, get_operator_list_for_select_input):
        hit = mock.Mock()
        hit.to_dict.return_value = {
            'key': '506 00I',
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'operator': '1',
                        'userRoute': '506'
                    }}]
                }
            }
        }
        get_base_query.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.source.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).route = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[hit])
        get_operator_list_for_select_input.return_value = [1, 2]
        result, operator_list = self.instance.get_available_routes(valid_operator_list=[1, 2, 3])
        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [1, 2])

    @mock.patch('esapi.helper.profile.get_operator_list_for_select_input')
    @mock.patch('esapi.helper.profile.ESProfileHelper.get_base_query')
    def test_get_available_routes_with_start_and_end_date(self, get_base_query, get_operator_list_for_select_input):
        hit = mock.Mock()
        hit.to_dict.return_value = {
            'key': '506 00I',
            'additionalInfo': {
                'hits': {
                    'hits': [{'_source': {
                        'operator': '1',
                        'userRoute': '506'
                    }}]
                }
            }
        }
        get_base_query.return_value = get_base_query
        get_base_query.__getitem__.return_value = get_base_query
        get_base_query.source.return_value = get_base_query
        get_base_query.filter.return_value = get_base_query
        get_base_query.execute.return_value = get_base_query
        type(get_base_query).aggregations = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).route = mock.PropertyMock(return_value=get_base_query)
        type(get_base_query).buckets = mock.PropertyMock(return_value=[hit])
        get_operator_list_for_select_input.return_value = [1, 2]
        result, operator_list = self.instance.get_available_routes(valid_operator_list=[1, 2, 3],
                                                                   start_date="2020-01-01", end_date="2020-03-01")
        self.assertDictEqual(result, {'1': {'506': ['506 00I']}})
        self.assertListEqual(operator_list, [1, 2])

    def test_get_base_profile_by_expedition_data_query(self):
        dates = [[""]]
        day_type = ['LABORAL']
        auth_route = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_profile_by_expedition_data,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_profile_by_expedition_data, dates,
                          day_type, auth_route, period, half_hour, valid_operator_list)
        auth_route = '506 00I'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_expedition_data,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_base_profile_by_expedition_data_query(dates, day_type, auth_route,
                                                                         period, half_hour,
                                                                         valid_operator_list, show_evasion=True)
        expected = {'query': {'bool': {'filter': [{'term': {'fulfillment': 'C'}}, {'terms': {'operator': [1, 2, 3]}},
                                                  {'term': {'route': '506 00I'}}, {'terms': {'dayType': ['LABORAL']}},
                                                  {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {'gte': '2018-01-01||/d', 'lte': '2018-01-02||/d', 'format': 'yyyy-MM-dd',
                                        'time_zone': '+00:00'}}}, {'term': {'notValid': 0}}]}},
                    '_source': ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId',
                                'expandedAlighting', 'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime',
                                'authStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                                'busStation', 'path', 'notValid', 'boardingWithAlighting', 'boarding',
                                'uniformDistributionMethod', 'expandedEvasionBoarding', 'expandedEvasionAlighting',
                                'expandedBoardingPlusExpandedEvasionBoarding',
                                'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
                                'evasionPercent', 'evasionType', 'passengerWithEvasionPerKmSection',
                                'capacityPerKmSection']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_profile_by_expedition_data(self):
        dates = [['2018-01-01', '2018-02-01']]
        result = self.instance.get_profile_by_expedition_data(dates, ['LABORAL'], 'route', [1, 2, 3],
                                                              [1, 2, 3], [1, 2, 3], show_evasion=True)
        expected = {'query': {'bool': {
            'filter': [{'term': {'fulfillment': 'C'}}, {'terms': {'operator': [1, 2, 3]}}, {'term': {'route': 'route'}},
                       {'terms': {'dayType': ['LABORAL']}}, {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                       {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                    'expeditionStartTime': {'gte': '2018-01-01||/d', 'lte': '2018-02-01||/d', 'format': 'yyyy-MM-dd',
                                            'time_zone': '+00:00'}}}, {'term': {'notValid': 0}}]}}, 'aggs': {
            'stops': {'terms': {'field': 'authStopCode.raw', 'size': 500},
                      'aggs': {'expandedAlighting': {'avg': {'field': 'expandedAlighting'}},
                               'expandedBoarding': {'avg': {'field': 'expandedBoarding'}},
                               'loadProfile': {'avg': {'field': 'loadProfile'}},
                               'maxLoadProfile': {'max': {'field': 'loadProfile'}},
                               'sumLoadProfile': {'sum': {'field': 'loadProfile'}},
                               'sumBusCapacity': {'sum': {'field': 'busCapacity'}}, 'busSaturation': {
                              'bucket_script': {'script': 'params.d / params.t',
                                                'buckets_path': {'d': 'sumLoadProfile', 't': 'sumBusCapacity'}}},
                               'pathDistance': {'top_hits': {'size': 1, '_source': ['stopDistanceFromPathStart']}},
                               'boardingWithAlighting': {'sum': {'field': 'boardingWithAlighting'}},
                               'boarding': {'sum': {'field': 'boarding'}},
                               'expandedEvasionBoarding': {'avg': {'field': 'expandedEvasionBoarding'}},
                               'expandedEvasionAlighting': {'avg': {'field': 'expandedEvasionAlighting'}},
                               'expandedBoardingPlusExpandedEvasionBoarding': {
                                   'avg': {'field': 'expandedBoardingPlusExpandedEvasionBoarding'}},
                               'expandedAlightingPlusExpandedEvasionAlighting': {
                                   'avg': {'field': 'expandedAlightingPlusExpandedEvasionAlighting'}},
                               'loadProfileWithEvasion': {'avg': {'field': 'loadProfileWithEvasion'}},
                               'maxLoadProfileWithEvasion': {'max': {'field': 'loadProfileWithEvasion'}},
                               'sumLoadProfileWithEvasion': {'sum': {'field': 'loadProfileWithEvasion'}},
                               'busSaturationWithEvasion': {'bucket_script': {'script': 'params.d / params.t',
                                                                              'buckets_path': {
                                                                                  'd': 'sumLoadProfileWithEvasion',
                                                                                  't': 'sumBusCapacity'}}},
                               'passengerWithEvasionPerKmSection': {
                                   'sum': {'field': 'passengerWithEvasionPerKmSection'}},
                               'capacityPerKmSection': {'sum': {'field': 'capacityPerKmSection'}}}},
            'stop': {'filter': {'term': {'busStation': 1}},
                     'aggs': {'station': {'terms': {'field': 'authStopCode.raw', 'size': 500}}}}}, 'from': 0, 'size': 0,
            '_source': ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId',
                        'expandedAlighting', 'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime',
                        'authStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                        'busStation', 'path', 'notValid', 'boardingWithAlighting', 'boarding',
                        'uniformDistributionMethod', 'expandedEvasionBoarding',
                        'expandedEvasionAlighting', 'expandedBoardingPlusExpandedEvasionBoarding',
                        'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
                        'evasionPercent', 'evasionType', 'passengerWithEvasionPerKmSection', 'capacityPerKmSection']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_base_profile_by_trajectory_data_query(self):
        dates = [[""]]
        day_type = ['LABORAL']
        auth_route = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryRouteParameterDoesNotExist, self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        auth_route = '506 00I'
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist,
                          self.instance.get_base_profile_by_trajectory_data_query,
                          dates, day_type, auth_route, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        result = self.instance.get_base_profile_by_trajectory_data_query(dates, day_type, auth_route,
                                                                         period, half_hour,
                                                                         valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'term': {'fulfillment': 'C'}}, {'terms': {'operator': [1, 2, 3]}},
                                                  {'term': {'route': '506 00I'}}, {'terms': {'dayType': ['LABORAL']}},
                                                  {'terms': {'timePeriodInStartTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStartTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {'gte': '2018-01-01||/d', 'lte': '2018-01-02||/d', 'format': 'yyyy-MM-dd',
                                        'time_zone': '+00:00'}}}]}},
                    '_source': ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId',
                                'expandedAlighting', 'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime',
                                'authStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                                'busStation', 'path', 'stopDistanceFromPathStart', 'expeditionStopTime', 'notValid',
                                'expandedEvasionBoarding', 'expandedEvasionAlighting',
                                'expandedBoardingPlusExpandedEvasionBoarding',
                                'expandedAlightingPlusExpandedEvasionAlighting', 'loadProfileWithEvasion',
                                'boardingWithAlighting']}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    @mock.patch('esapi.helper.basehelper.ElasticSearchHelper._get_available_days')
    def test_get_available_days_between_dates(self, _get_available_days):
        start_date = '2018-01-01'
        end_date = '2018-01-05'
        _get_available_days.return_value = [
            '2018-01-03',
            '2018-02-05',
        ]
        result = self.instance.get_available_days_between_dates(start_date, end_date)
        self.assertIsInstance(result, list)
        self.assertListEqual(result, ['2018-01-03'])

    def test_get_profile_by_multiple_stop_data(self):
        dates = []
        day_type = ['LABORAL']
        stop_code = ''
        period = [1, 2, 3]
        half_hour = [1, 2, 3]
        valid_operator_list = []
        self.assertRaises(ESQueryDateRangeParametersDoesNotExist, self.instance.get_profile_by_multiple_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        dates = [['2018-01-01', '2018-01-02']]
        self.assertRaises(ESQueryOperatorParameterDoesNotExist, self.instance.get_profile_by_multiple_stop_data, dates,
                          day_type, stop_code, period, half_hour, valid_operator_list)
        valid_operator_list = [1, 2, 3]
        self.assertRaises(ESQueryStopParameterDoesNotExist, self.instance.get_profile_by_multiple_stop_data,
                          dates, day_type, stop_code, period, half_hour, valid_operator_list)
        stop_code = 'PA433'
        result = self.instance.get_profile_by_multiple_stop_data(dates, day_type, stop_code, period, half_hour,
                                                                 valid_operator_list)
        expected = {'query': {'bool': {'filter': [{'term': {'fulfillment': 'C'}}, {'terms': {'operator': [1, 2, 3]}},
                                                  {'terms': {'dayType': ['LABORAL']}},
                                                  {'terms': {'timePeriodInStopTime': [1, 2, 3]}},
                                                  {'terms': {'halfHourInStopTime': [1, 2, 3]}}, {'range': {
                'expeditionStartTime': {'gte': '2018-01-01||/d', 'lte': '2018-01-02||/d', 'format': 'yyyy-MM-dd',
                                        'time_zone': '+00:00'}}}], 'must': [{'terms': {'authStopCode.raw': 'PA433'}}]}},
                    'aggs': {'stops': {'terms': {'field': 'authStopCode.raw', 'size': 1000},
                                       'aggs': {'expandedAlighting': {'avg': {'field': 'expandedAlighting'}},
                                                'expandedBoarding': {'avg': {'field': 'expandedBoarding'}},
                                                'sumExpandedAlighting': {'sum': {'field': 'expandedAlighting'}},
                                                'sumExpandedBoarding': {'sum': {'field': 'expandedBoarding'}},
                                                'loadProfile': {'avg': {'field': 'loadProfile'}},
                                                'maxLoadProfile': {'max': {'field': 'loadProfile'}},
                                                'sumLoadProfile': {'sum': {'field': 'loadProfile'}},
                                                'sumBusCapacity': {'sum': {'field': 'busCapacity'}}, 'busSaturation': {
                                               'bucket_script': {'script': 'params.d / params.t',
                                                                 'buckets_path': {'d': 'sumLoadProfile',
                                                                                  't': 'sumBusCapacity'}}},
                                                'userStopCode': {'top_hits': {'size': 1, '_source': ['userStopCode']}},
                                                'userStopName': {'top_hits': {'size': 1, '_source': ['userStopName']}},
                                                'busCapacity': {'avg': {'field': 'busCapacity'}},
                                                'tripsCount': {'value_count': {'field': 'expandedAlighting'}},
                                                'expandedEvasionBoarding': {
                                                    'avg': {'field': 'expandedEvasionBoarding'}},
                                                'expandedEvasionAlighting': {
                                                    'avg': {'field': 'expandedEvasionAlighting'}},
                                                'expandedBoardingPlusExpandedEvasionBoarding': {
                                                    'avg': {'field': 'expandedBoardingPlusExpandedEvasionBoarding'}},
                                                'expandedAlightingPlusExpandedEvasionAlighting': {
                                                    'avg': {'field': 'expandedAlightingPlusExpandedEvasionAlighting'}},
                                                'loadProfileWithEvasion': {'avg': {'field': 'loadProfileWithEvasion'}},
                                                'boardingWithAlighting': {'sum': {'field': 'boardingWithAlighting'}}}}},
                    'from': 0, 'size': 0}

        self.assertIsInstance(result, Search)
        self.assertDictEqual(result.to_dict(), expected)

    def test_get_all_auth_routes(self):
        expected = {'from': 0, 'aggs': {'route': {'terms': {'field': 'route', 'size': 5000}}}, 'size': 0}
        result = self.instance.get_all_auth_routes().to_dict()
        self.assertDictEqual(result, expected)

    def test_get_all_time_periods(self):
        expected_query = {'aggs': {'time_periods_per_file': {'terms': {'field': 'path', 'size': 5000}, 'aggs': {
            'time_periods_0': {'terms': {'field': 'timePeriodInStartTime'}},
            'time_periods_1': {'terms': {'field': 'timePeriodInStopTime'}}}}}, 'from': 0, 'size': 0}

        result = self.instance.get_all_time_periods().to_dict()
        self.assertEqual(expected_query, result)
