import json
from unittest import mock

from django.urls import reverse

from esapi.errors import ESQueryResultEmpty, ESQueryDateParametersDoesNotExist
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from testhelper.helper import TestHelper


class ResumeDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:resumeTripData')
        self.data = {
            'dates': "[['']]",
            'dayType[]': [],
            'period[]': [],
            'origin[]': [],
            'destination[]': []
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        self.data['authRoute'] = '506 00I'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_get(self, make_multisearch_query_for_aggs):
        histogram = mock.Mock()
        indicators = mock.Mock()
        type(histogram).hits = histogram
        type(histogram).total = 1
        histogram.to_dict.return_value = {}
        indicators.to_dict.return_value = {}
        make_multisearch_query_for_aggs.return_value = (histogram, indicators)
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        expected = {
            "indicators": {},
            "histogram": {}
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_without_result(self, make_multisearch_query_for_aggs):
        histogram = mock.Mock()
        indicators = mock.Mock()
        type(histogram).hits = histogram
        type(histogram).total = 0
        make_multisearch_query_for_aggs.return_value = (histogram, indicators)
        data = {
            'dates': '[["2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class MapDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:tripMapData')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': [],
            'boardingPeriod[]': [],
        }
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_get(self, make_multisearch_query_for_aggs):
        make_multisearch_query_for_aggs.return_value = make_multisearch_query_for_aggs
        make_multisearch_query_for_aggs.to_dict.return_value = {}
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        expected = {
            "KPIs": [{"text": "Tiempo de viaje", "id": "tviaje"}, {"text": "Distancia en ruta", "id": "distancia_ruta"},
                     {"text": "Distancia euclidiana", "id": "distancia_eucl"},
                     {"text": "N\u00famero de etapas", "id": "n_etapas"}, {"text": "Cantidad de datos", "id": "count"}],
            "sectors": {"Lo Barnechea": [202, 642], "Centro": [267, 276, 285, 286], "Providencia": [175, 176, 179],
                        "Quilicura": [557, 831], "Vitacura": [191, 192, 193, 195, 196], "Las Condes": [207, 215, 216]},
            "map": {}
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01", "2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class AvailableDaysTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:availableTripDays')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': [],
            'boardingPeriod[]': [],
        }
        self.available_date = '2018-01-01'

    @mock.patch('esapi.helper.trip.ESTripHelper.get_available_days')
    def test_exec_elasticsearch_query_get(self, get_available_days):
        get_available_days.return_value = 'days'
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [],
            'origin[]': [1, 2, 3],
            'destination[]': [3, 2, 1]
        }
        expected = {'availableDays': 'days', 'info': []}
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)


class LargeTravelDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:largeTravelData')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': [],
            'period[]': [],
            'stages[]': [],
            'originOrDestination': '',
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_get(self, make_multisearch_query_for_aggs):
        make_multisearch_query_for_aggs.return_value = make_multisearch_query_for_aggs
        make_multisearch_query_for_aggs.to_dict.return_value = {}
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'stages[]': [1, 2, 3],
            'originOrDestination': '',
        }
        expected = {
            "large": {}
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'stages[]': [1, 2, 3],
            'originOrDestination': '',
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class FromToMapDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:fromToMapData')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': [],
            'period[]': [],
            'halfHour[]': [],
            'stages[]': [],
            'transportModes[]': [],
            'originZones[]': [],
            'destinationZones[]': [],
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_get(self, make_multisearch_query_for_aggs):
        origin_zone = mock.Mock()
        destination_zone = mock.Mock()
        origin_zone.to_dict.return_value = {}
        destination_zone.to_dict.return_value = {}
        make_multisearch_query_for_aggs.return_value = (origin_zone, destination_zone)
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'stages[]': [1, 2, 3],
            'originOrDestination': '',
        }
        expected = {
            'destination_zone': {},
            'origin_zone': {}
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.trip.ESTripHelper.make_multisearch_query_for_aggs')
    def test_exec_elasticsearch_query_without_result(self, make_multisearch_query_for_aggs):
        origin_zone = mock.Mock()
        destination_zone = mock.Mock()
        origin_zone.to_dict.return_value = {}
        destination_zone.to_dict.return_value = {}
        type(origin_zone).hits = mock.PropertyMock(return_value=origin_zone)
        type(origin_zone).total = mock.PropertyMock(return_value=0)
        type(destination_zone).total = mock.PropertyMock(return_value=destination_zone)
        type(destination_zone).total = mock.PropertyMock(return_value=0)
        make_multisearch_query_for_aggs.return_value = (origin_zone, destination_zone)
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'stages[]': [1, 2, 3],
            'originOrDestination': '',
        }
        response = self.client.get(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'stages[]': [1, 2, 3],
            'originOrDestination': '',
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class StrategiesDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:tripStrategiesData')
        self.data = {
            'dates': '[[""]]',
            'daytypes[]': [],
            'period[]': [],
            'halfHour[]': [],
            'originZones[]': [],
            'destinationZones[]': [],
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.trip.ESTripHelper.get_strategies_data')
    def test_exec_elasticsearch_query_get(self, get_strategies_data):
        get_strategies_data.return_value = get_strategies_data
        get_strategies_data.execute.return_value = get_strategies_data
        first = mock.Mock()
        second = mock.Mock()
        third = mock.Mock()
        fourth = mock.Mock()
        type(fourth).key = mock.PropertyMock(return_value='key4')
        type(fourth).expansion_factor = mock.PropertyMock(return_value=fourth)
        type(fourth).value = mock.PropertyMock(return_value=1)

        type(third).fourth = mock.PropertyMock(return_value=third)
        type(third).buckets = mock.PropertyMock(return_value=[fourth])
        type(third).key = mock.PropertyMock(return_value='key3')

        type(second).third = mock.PropertyMock(return_value=second)
        type(second).buckets = mock.PropertyMock(return_value=[third])
        type(second).key = mock.PropertyMock(return_value='key2')

        type(first).second = mock.PropertyMock(return_value=first)
        type(first).buckets = mock.PropertyMock(return_value=[second])
        type(first).key = mock.PropertyMock(return_value='key')

        type(get_strategies_data).aggregations = mock.PropertyMock(return_value=get_strategies_data)
        type(get_strategies_data).strategies_without_metro_or_metrotren = mock.PropertyMock(
            return_value=get_strategies_data)
        type(get_strategies_data).first = mock.PropertyMock(return_value=get_strategies_data)
        type(get_strategies_data).buckets = mock.PropertyMock(return_value=[first])
        type(get_strategies_data).expansion_factor = mock.PropertyMock(return_value=get_strategies_data)
        type(get_strategies_data).value = mock.PropertyMock(return_value=1)
        type(get_strategies_data).hits = mock.PropertyMock(return_value=get_strategies_data)
        type(get_strategies_data).total = mock.PropertyMock(return_value=10)
        get_strategies_data.__dir__ = mock.Mock(
            return_value=['expansion_factor', 'strategies_without_metro_or_metrotren'])
        data = {
            'dates': '[["2018-01-01"]]',
            'daytypes[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'halfHour[]': [1, 2, 3],
            'originZones[]': [1, 2, 3],
            'destinationZones[]': [3, 2, 1],
        }
        expected = {
            "strategies": {
                "key": {
                    "key2": {
                        "key3": {
                            "key4": 1
                        }
                    }
                }
            },
            "expansionFactor": 1,
            "docCount": 10
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'daytypes[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'halfHour[]': [1, 2, 3],
            'originZones[]': [1, 2, 3],
            'destinationZones[]': [3, 2, 1],
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class TransfersDataTest(TestHelper):
    fixtures = ['timeperioddates', 'timeperiods', 'operators', 'daytypes']

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:transfersData')
        self.data = {
            'dates': '[[""]]',
            'stopCode': '',
            'period[]': [],
            'dayType[]': [],
            'halfHour[]': [],
        }
        self.available_date = '2018-01-01'

    def test_wrong_dates(self):
        self.data['dates'] = '[[]]'
        response = self.client.get(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())

    @mock.patch('esapi.helper.stop.ESStopHelper.get_stop_info')
    @mock.patch('esapi.helper.trip.ESTripHelper.get_transfers_data')
    def test_exec_elasticsearch_query_get(self, get_transfers_data, get_stop_info):
        get_stop_info.return_value = {}
        get_transfers_data.return_value = get_transfers_data
        get_transfers_data.__getitem__.return_value = get_transfers_data
        get_transfers_data.execute.return_value = get_transfers_data
        type(get_transfers_data).aggregations = mock.PropertyMock(return_value=get_transfers_data)

        step = mock.Mock()
        from_bucket = mock.Mock()
        to_bucket = mock.Mock()
        type(to_bucket).doc_count = mock.PropertyMock(return_value=1)
        type(to_bucket).key = mock.PropertyMock(return_value='-')

        type(from_bucket).route_to = mock.PropertyMock(return_value=from_bucket)
        type(from_bucket).buckets = mock.PropertyMock(return_value=[to_bucket])
        type(from_bucket).key = mock.PropertyMock(return_value='key2')
        type(from_bucket).doc_count = mock.PropertyMock(return_value=2)

        type(step).route_from = mock.PropertyMock(return_value=step)
        type(step).buckets = mock.PropertyMock(return_value=[from_bucket])

        type(get_transfers_data).first_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).first_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).first_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).fourth_transfer_is_end = mock.PropertyMock(return_value=step)
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'halfHour[]': [1, 2, 3],
            'stopCode': 'stop_code',
        }
        expected = {
            "stopInfo": {},
            "data": {
                "end": {
                    "key2": 5
                },
                "-": {
                    "key2": 6
                }
            }
        }
        response = self.client.get(self.url, data)
        self.assertNotContains(response, 'status')
        self.assertJSONEqual(response.content, expected)

    @mock.patch('esapi.helper.stop.ESStopHelper.get_stop_info')
    @mock.patch('esapi.helper.trip.ESTripHelper.get_transfers_data')
    def test_exec_elasticsearch_query_get_without_result(self, get_transfers_data, get_stop_info):
        get_stop_info.return_value = {}
        get_transfers_data.return_value = get_transfers_data
        get_transfers_data.__getitem__.return_value = get_transfers_data
        get_transfers_data.execute.return_value = get_transfers_data
        type(get_transfers_data).aggregations = mock.PropertyMock(return_value=get_transfers_data)

        step = mock.Mock()
        from_bucket = mock.Mock()

        type(from_bucket).route_to = mock.PropertyMock(return_value=from_bucket)
        type(from_bucket).buckets = mock.PropertyMock(return_value=[])

        type(step).route_from = mock.PropertyMock(return_value=step)
        type(step).buckets = mock.PropertyMock(return_value=[])

        type(get_transfers_data).first_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer = mock.PropertyMock(return_value=step)
        type(get_transfers_data).first_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer_to_subway = mock.PropertyMock(return_value=step)
        type(get_transfers_data).first_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).second_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).third_transfer_is_end = mock.PropertyMock(return_value=step)
        type(get_transfers_data).fourth_transfer_is_end = mock.PropertyMock(return_value=step)
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'halfHour[]': [1, 2, 3],
            'stopCode': 'stop_code',
        }
        response = self.client.get(self.url, data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryResultEmpty().get_status_response())
        self.assertContains(response, 'status')

    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'period[]': [1, 2, 3],
            'halfHour[]': [1, 2, 3],
            'stopCode': 'stop_code',
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())


class PostProductTripsBetweenZonesTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:postProductTripsBetweenZones')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': []
        }

    @mock.patch('esapi.helper.trip.ESTripHelper.get_post_products_trip_between_zone_data_query')
    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager, get_post_products_trip_between_zone_data_query):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        get_post_products_trip_between_zone_data_query.return_value = get_post_products_trip_between_zone_data_query
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL']
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())

    def test_wrong_dats(self):
        self.data['dates'] = '[[]]'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())


class PostProductTripsBoardingAndAlightingTest(TestHelper):

    def setUp(self):
        self.client = self.create_logged_client_with_global_permission()
        self.url = reverse('esapi:postProductBoardingAndAlighting')
        self.data = {
            'dates': '[[""]]',
            'dayType[]': []
        }

    @mock.patch('esapi.helper.trip.ESTripHelper.get_post_products_boarding_and_alighting_data_query')
    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post(self, exporter_manager, get_post_products_boarding_and_alighting_data_query):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        get_post_products_boarding_and_alighting_data_query.return_value = get_post_products_boarding_and_alighting_data_query
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
            'exportButton2': True
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())

    @mock.patch('esapi.helper.trip.ESTripHelper.get_post_products_boarding_and_alighting_data_query')
    @mock.patch('esapi.views.trip.ExporterManager')
    def test_exec_elasticsearch_query_post_without_service(self, exporter_manager,
                                                           get_post_products_boarding_and_alighting_without_service_data_query):
        exporter_manager.return_value = exporter_manager
        exporter_manager.export_data.return_value = None
        get_post_products_boarding_and_alighting_without_service_data_query.return_value = get_post_products_boarding_and_alighting_without_service_data_query
        data = {
            'dates': '[["2018-01-01","2018-01-01"]]',
            'dayType[]': ['LABORAL'],
        }
        response = self.client.post(self.url, data)
        self.assertContains(response, 'status')
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ExporterDataHasBeenEnqueuedMessage().get_status_response())

    def test_wrong_dats(self):
        self.data['dates'] = '[[]]'
        response = self.client.post(self.url, self.data)
        status = json.dumps(json.loads(response.content)['status'])
        self.assertJSONEqual(status, ESQueryDateParametersDoesNotExist().get_status_response())
