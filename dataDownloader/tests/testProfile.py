from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import profile


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestProfileByExpeditionData(TestCase):

    def test_get_routes(self):
        es_query = {"query": {"bool": {
            "filter": [{"terms": {"operator": []}}, {"term": {"route": "T501 00I"}},
                       {"terms": {"dayType": ["0"]}}, {"bool": {
                    "should": [
                        {"range": {
                            "expeditionStartTime": {"gte": "2019-08-05||/d", "lte": "2019-08-06||/d",
                                                    "format": "yyyy-MM-dd", "time_zone": "+00:00"}}},
                        {"range": {
                            "expeditionStartTime": {"gte": "2019-08-08||/d", "lte": "2019-08-11||/d",
                                                    "format": "yyyy-MM-dd", "time_zone": "+00:00"}}}]}},
                       {"term": {"notValid": 0}}]}},
            "_source": ["busCapacity"]}

        profile_obj = profile.ProfileByExpeditionData(es_query)
        self.assertEqual(["T501 00I"], profile_obj.get_routes())

    def test_get_date_range_from_list_of_dates(self):
        es_query = {"query": {"bool": {
            "filter": [{"terms": {"operator": [1, 2, 3, 4, 5, 6, 7, 8, 9]}}, {"term": {"route": "T501 00I"}},
                       {"terms": {"dayType": ["0"]}}, {"terms": {"timePeriodInStartTime": ["4"]}}, {"bool": {"should": [
                    {"range": {"expeditionStartTime": {"gte": "2019-08-05||/d", "lte": "2019-08-06||/d",
                                                       "format": "yyyy-MM-dd", "time_zone": "+00:00"}}}, {"range": {
                        "expeditionStartTime": {"gte": "2019-08-08||/d", "lte": "2019-08-11||/d",
                                                "format": "yyyy-MM-dd", "time_zone": "+00:00"}}}]}},
                       {"term": {"notValid": 0}}]}},
            "_source": ["busCapacity"]}

        profile_obj = profile.ProfileByExpeditionData(es_query)
        self.assertEqual(("2019-08-05", "2019-08-11"), profile_obj.get_date_range())

    def test_get_date_range_from_range_key(self):
        es_query = {"query": {"bool": {
            "filter": [{"terms": {"operator": [1, 2, 3, 4, 5, 6, 7]}}, {"term": {"route": "B13 00I"}}, {"range": {
                "expeditionStartTime": {"gte": "2020-03-07||/d", "lte": "2020-03-10||/d", "format": "yyyy-MM-dd",
                                        "time_zone": "+00:00"}}}, {"term": {"notValid": 0}}]}},
            "_source": ["busCapacity", "licensePlate", "route", "loadProfile", "expeditionDayId",
                        "expandedAlighting", "expandedBoarding", "expeditionStartTime", "expeditionEndTime",
                        "authStopCode", "timePeriodInStartTime", "dayType", "timePeriodInStopTime",
                        "busStation", "path", "notValid"]}

        profile_obj = profile.ProfileByExpeditionData(es_query)
        self.assertEqual(("2020-03-07", "2020-03-10"), profile_obj.get_date_range())
