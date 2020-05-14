from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import profile


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestProfileByExpeditionData(TestCase):

    def setUp(self):
        es_query = {'query': {'bool': {
            'filter': [{'terms': {'operator': [1, 2, 3, 4, 5, 6, 7, 8, 9]}}, {'term': {'route': 'T501 00I'}},
                       {'terms': {'dayType': ['0']}}, {'terms': {'timePeriodInStartTime': ['4']}}, {'bool': {'should': [
                    {'range': {'expeditionStartTime': {'gte': '2019-08-05||/d', 'lte': '2019-08-06||/d',
                                                       'format': 'yyyy-MM-dd', 'time_zone': '+00:00'}}}, {'range': {
                        'expeditionStartTime': {'gte': '2019-08-08||/d', 'lte': '2019-08-11||/d',
                                                'format': 'yyyy-MM-dd', 'time_zone': '+00:00'}}}]}},
                       {'term': {'notValid': 0}}]}},
            '_source': ['busCapacity', 'licensePlate', 'route', 'loadProfile', 'expeditionDayId',
                        'expandedAlighting', 'expandedBoarding', 'expeditionStartTime', 'expeditionEndTime',
                        'authStopCode', 'timePeriodInStartTime', 'dayType', 'timePeriodInStopTime',
                        'busStation', 'path', 'notValid']}

        self.profile = profile.ProfileByExpeditionData(es_query)

    def test_get_routes(self):
        self.assertEqual(['T501 00I'], self.profile.get_routes())

    def test_get_date_range(self):
        self.assertEqual(('2019-08-05', '2019-08-11'), self.profile.get_date_range())

    def test_get_filters(self):
        print(self.profile.get_filters())
