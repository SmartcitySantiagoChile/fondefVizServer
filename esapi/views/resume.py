from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views.generic import View

from esapi.errors import ESQueryResultEmpty, ESQueryDateParametersDoesNotExist, FondefVizError
from esapi.helper.resume import ESResumeStatisticHelper
# to translate variable to user name
from esapi.utils import get_dates_from_request
from localinfo.helper import get_calendar_info

DICTIONARY = {
    'date': {'name': 'Día', 'order': 1},
    'transactionWithoutRoute': {'name': 'transacciones sin servicio asignado', 'chartName': 'Sin servicio asignado',
                                'order': 2},
    'transactionWithRoute': {'name': 'Transacciones con servicio asignado', 'chartName': 'Con servicio asignado',
                             'order': 3},
    'transactionNumber': {'name': 'Número de transacciones', 'chartName': '', 'order': 4},
    'transactionOnTrainNumber': {'name': 'Porcentaje de transacciones en metrotren', 'chartName': 'Metrotren', 'order': 5},
    'transactionOnMetroNumber': {'name': 'Porcentaje de transacciones en metro', 'chartName': 'Metro', 'order': 6},
    'transactionOnBusNumber': {'name': 'Porcentaje de transacciones en bus', 'chartName': 'Bus', 'order': 7},
    'transactionOnBusStation': {'name': 'Porcentaje de transacciones en zona paga', 'chartName': 'Zona paga', 'order': 8},

    'averageVelocityInAfternoonRushTrips': {'name': 'Velocidad prom. de viajes en punta tarde (Km/H)', 'chartName': '',
                                            'order': 9},
    'averageTimeInAfternoonRushTrips': {'name': 'Tiempo prom. de viajes en punta tarde', 'chartName': '', 'order': 10},
    'averageDistanceInAfternoonRushTrips': {'name': 'Distancia prom. de viajes en punta tarde (mts)', 'chartName': '',
                                            'order': 11},
    'tripNumberInAfternoonRushHour': {'name': 'Número de viajes en punta tarde', 'chartName': '', 'order': 12},

    'averageVelocityInMorningRushTrips': {'name': 'Velocidad prom. de viaje en punta mañana (Km/H)', 'chartName': '',
                                          'order': 13},
    'averageTimeInMorningRushTrips': {'name': 'Tiempo prom. de viaje en punta mañana', 'chartName': '', 'order': 14},
    'averageDistanceInMorningRushTrips': {'name': 'Distancia prom. de viajes en punta mañana (mts)', 'chartName': '',
                                          'order': 15},
    'tripNumberInMorningRushHour': {'name': 'Número de viajes en punta mañana', 'chartName': '', 'order': 16},

    'licensePlateNumber': {'name': 'Número de patentes', 'chartName': '', 'order': 17},
    'GPSPointsNumber': {'name': 'Número de pulsos GPS', 'chartName': '', 'order': 18},
    'GPSNumberWithRoute': {'name': 'Número de GPS con servicio asignado', 'chartName': '', 'order': 19},
    'GPSNumberWithoutRoute': {'name': 'Número de pulsos GPS sin servicio asignado', 'chartName': '', 'order': 20},
    'averageTimeBetweenGPSPoints': {'name': 'Tiempo prom. entre pulsos GPS', 'chartName': '', 'order': 40},

    'tripsWithOneStage': {'name': 'Porcentaje de viajes con una etapa', 'chartName': '1 etapa', 'order': 22},
    'tripsWithTwoStages': {'name': 'Porcentaje de viajes con dos etapas', 'chartName': '2 etapas', 'order': 23},
    'tripsWithThreeStages': {'name': 'Porcentaje de viajes con tres etapas', 'chartName': '3 etapas', 'order': 24},
    'tripsWithFourStages': {'name': 'Porcentaje de viajes con cuatro etapas', 'chartName': '4 etapas', 'order': 25},
    'tripsWithFiveOrMoreStages': {'name': 'Porcentaje de viajes con cinco o más etapas', 'chartName': '5 o más etapas',
                                  'order': 26},
    'tripsWithOnlyMetro': {'name': 'Porcentaje de viajes solo en metro', 'chartName': '', 'order': 27},

    'stagesWithBusAlighting': {'name': 'Porcentaje de etapas con bajada estimada en bus', 'chartName': 'Bus',
                               'order': 28},
    'stagesWithTrainAlighting': {'name': 'Porcentaje de etapas con bajada estimada en metrotren',
                                 'chartName': 'Metrotren', 'order': 29},
    'stagesWithMetroAlighting': {'name': 'Porcentaje de etapas con bajada estimada en metro', 'chartName': 'Metro',
                                 'order': 30},
    'stagesWithBusStationAlighting': {'name': 'Porcentaje de etapas con bajada estimada en zona paga',
                                      'chartName': 'Zona paga', 'order': 45},

    'expeditionNumber': {'name': 'Número de expediciones', 'chartName': '', 'order': 31},
    'maxExpeditionTime': {'name': 'Tiempo de expedición máximo', 'chartName': '', 'order': 32},
    'minExpeditionTime': {'name': 'Tiempo de expedición mínimo', 'chartName': '', 'order': 33},
    'averageExpeditionTime': {'name': 'Tiempo prom. de expedición', 'chartName': '', 'order': 34},

    'smartcardNumber': {'name': 'Número de tarjetas', 'chartName': '', 'order': 35},
    'dayType': {'name': 'Tipo de día', 'chartName': '', 'order': 36},

    'tripNumber': {'name': 'Número de viajes válido', 'chartName': '', 'order': 37},
    'averageTimeOfTrips': {'name': 'Tiempo promedio de viajes', 'chartName': '', 'order': 38},
    'averageVelocityOfTrips': {'name': 'Velocidad prom. de viajes (Km/H)', 'chartName': '', 'order': 39},
    'averageDistanceOfTrips': {'name': 'Distancia promedio de viajes (mts)', 'chartName': '', 'order': 41},

    'tripsThatUseMetro': {'name': 'Porcentaje de viajes que usan metro', 'chartName': '', 'order': 42},
    'tripsWithoutLastAlighting': {'name': 'Porcentaje de viajes sin última bajada', 'chartName': '', 'order': 44},

    'transactionInMorningRushHour': {'name': 'Número de validaciones bip! en punta mañana', 'chartName': '',
                                     'order': 45},
    'transactionInAfternoonRushHour': {'name': 'Número de validaciones bip! en punta tarde', 'chartName': '',
                                       'order': 46},
    'alightingNumber': {'name': 'Número de bajadas (suma sobre expansión zona-período)', 'chartName': '', 'order': 47},
    'alightingNumberInMorningRushHour': {
        'name': 'Número de bajadas en punta mañana (suma sobre expansión zona-período)', 'chartName': '', 'order': 48},
    'alightingNumberInAfternoonRushHour': {
        'name': 'Número de bajadas en punta tarde (suma sobre expansión zona-período)', 'chartName': '', 'order': 49},

    'stopsNumberWithTypeE': {'name': 'N° de paradas de tipo E', 'chartName': '', 'order': 50},
    'stopsNumberWithTypeT': {'name': 'N° de paradas de tipo T', 'chartName': '', 'order': 51},
    'stopsNumberWithTypeL': {'name': 'N° de paradas de tipo L', 'chartName': '', 'order': 52},
    'stopsNumberWithTypeI': {'name': 'N° de paradas de tipo I', 'chartName': '', 'order': 53},
    'transactionNumberInStopsWithTypeE': {'name': 'N° de validaciones en paraderos de tipo E', 'chartName': '',
                                          'order': 54},
    'transactionNumberInStopsWithTypeT': {'name': 'N° de validaciones en paraderos de tipo T', 'chartName': '',
                                          'order': 55},
    'transactionNumberInStopsWithTypeL': {'name': 'N° de validaciones en paraderos de tipo L', 'chartName': '',
                                          'order': 56},
    'transactionNumberInStopsWithTypeI': {'name': 'N° de validaciones en paraderos de tipo I', 'chartName': '',
                                          'order': 57},

    'firstStopWithMoreValidations': {'name': 'Paradero con más validaciones', 'chartName': '', 'order': 58},
    'secondStopWithMoreValidations': {'name': 'Segundo paradero con más validaciones', 'chartName': '', 'order': 59},
    'thirdStopWithMoreValidations': {'name': 'Tercer paradero con más validaciones', 'chartName': '', 'order': 60},
    'fourthStopWithMoreValidations': {'name': 'Cuarto paradero con más validaciones', 'chartName': '', 'order': 61},
    'fifthStopWithMoreValidations': {'name': 'Quinto paradero con más validaciones', 'chartName': '', 'order': 62},
    'sixthStopWithMoreValidations': {'name': 'Sexto paradero con más validaciones', 'chartName': '', 'order': 63},
    'seventhStopWithMoreValidations': {'name': 'Séptimo paradero con más validaciones', 'chartName': '', 'order': 64},
    'eighthStopWithMoreValidations': {'name': 'Octavo paradero con más validaciones', 'chartName': '', 'order': 65},
    'ninethStopWithMoreValidations': {'name': 'Noveno paradero con más validaciones', 'chartName': '', 'order': 66},
    'tenthStopWithMoreValidations': {'name': 'Décimo paradero con más validaciones', 'chartName': '', 'order': 67},
    'transactionNumberInFirstStopWithMoreValidations': {'name': 'N° de validaciones en paradero con más validaciones',
                                                        'chartName': '', 'order': 68},
    'transactionNumberInSecondStopWithMoreValidations': {
        'name': 'N° de validaciones en segundo paradero con más validaciones', 'chartName': '', 'order': 69},
    'transactionNumberInThirdStopWithMoreValidations': {
        'name': 'N° de validaciones en tercer paradero con más validaciones', 'chartName': '', 'order': 70},
    'transactionNumberInFourthStopWithMoreValidations': {
        'name': 'N° de validaciones en cuarto paradero con más validaciones', 'chartName': '', 'order': 71},
    'transactionNumberInFifthStopWithMoreValidations': {
        'name': 'N° de validaciones en quinto paradero con más validaciones', 'chartName': '', 'order': 72},
    'transactionNumberInSixthStopWithMoreValidations': {
        'name': 'N° de validaciones en sexto paradero con más validaciones', 'chartName': '', 'order': 73},
    'transactionNumberInSeventhStopWithMoreValidations': {
        'name': 'N° de validaciones en séptimo paradero con más validaciones', 'chartName': '', 'order': 74},
    'transactionNumberInEighthStopWithMoreValidations': {
        'name': 'N° de validaciones en octavo paradero con más validaciones', 'chartName': '', 'order': 75},
    'transactionNumberInNinethStopWithMoreValidations': {
        'name': 'N° de validaciones en noveno paradero con más validaciones', 'chartName': '', 'order': 76},
    'transactionNumberInTenthStopWithMoreValidations': {
        'name': 'N° de validaciones en décimo paradero con más validaciones', 'chartName': '', 'order': 77},

    'firstBusStopWithMoreValidations': {'name': 'Paradero de bus con más validaciones', 'chartName': '', 'order': 78},
    'secondBusStopWithMoreValidations': {'name': 'Segundo paradero de bus con más validaciones', 'chartName': '',
                                         'order': 79},
    'thirdBusStopWithMoreValidations': {'name': 'Tercer paradero de bus con más validaciones', 'chartName': '',
                                        'order': 80},
    'fourthBusStopWithMoreValidations': {'name': 'Cuarto paradero de bus con más validaciones', 'chartName': '',
                                         'order': 81},
    'fifthBusStopWithMoreValidations': {'name': 'Quinto paradero de bus con más validaciones', 'chartName': '',
                                        'order': 82},
    'sixthBusStopWithMoreValidations': {'name': 'Sexto paradero de bus con más validaciones', 'chartName': '',
                                        'order': 83},
    'seventhBusStopWithMoreValidations': {'name': 'Séptimo paradero de bus con más validaciones', 'chartName': '',
                                          'order': 84},
    'eighthBusStopWithMoreValidations': {'name': 'Octavo paradero de bus con más validaciones', 'chartName': '',
                                         'order': 85},
    'ninethBusStopWithMoreValidations': {'name': 'Noveno paradero de bus con más validaciones', 'chartName': '',
                                         'order': 86},
    'tenthBusStopWithMoreValidations': {'name': 'Décimo paradero de bus con más validaciones', 'chartName': '',
                                        'order': 87},
    'transactionNumberInFirstBusStopWithMoreValidations': {
        'name': 'N° de validaciones en paradero de bus con más validaciones', 'chartName': '', 'order': 88},
    'transactionNumberInSecondBusStopWithMoreValidations': {
        'name': 'N° de validaciones en segundo paradero de bus con más validaciones', 'chartName': '', 'order': 89},
    'transactionNumberInThirdBusStopWithMoreValidations': {
        'name': 'N° de validaciones en tercer paradero de bus con más validaciones', 'chartName': '', 'order': 90},
    'transactionNumberInFourthBusStopWithMoreValidations': {
        'name': 'N° de validaciones en cuarto paradero de bus con más validaciones', 'chartName': '', 'order': 91},
    'transactionNumberInFifthBusStopWithMoreValidations': {
        'name': 'N° de validaciones en quinto paradero de bus con más validaciones', 'chartName': '', 'order': 92},
    'transactionNumberInSixthBusStopWithMoreValidations': {
        'name': 'N° de validaciones en sexto paradero de bus con más validaciones', 'chartName': '', 'order': 93},
    'transactionNumberInSeventhBusStopWithMoreValidations': {
        'name': 'N° de validaciones en séptimo paradero de bus con más validaciones', 'chartName': '', 'order': 94},
    'transactionNumberInEighthBusStopWithMoreValidations': {
        'name': 'N° de validaciones en octavo paradero de bus con más validaciones', 'chartName': '', 'order': 95},
    'transactionNumberInNinethBusStopWithMoreValidations': {
        'name': 'N° de validaciones en noveno paradero de bus con más validaciones', 'chartName': '', 'order': 96},
    'transactionNumberInTenthBusStopWithMoreValidations': {
        'name': 'N° de validaciones en décimo paradero de bus con más validaciones', 'chartName': '', 'order': 97},

    'version': {'name': 'versión de ADATRAP con la que se procesó el día', 'chartName': '', 'order': 98},
}


class GlobalData(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def transform_data(self, es_query):
        """ transform ES answer to something util to web client """
        keys = {
            'date': 0
        }
        header = [DICTIONARY['date']['name']]
        identifiers = ['date']
        chart_names = ['Día']
        answer = []
        for hit in es_query.scan():
            hit_row = hit.to_dict()
            row = list(range(len(list(hit_row.keys()))))
            for key, value in hit_row.items():
                if key not in list(keys.keys()):
                    keys[key] = len(header)
                    header.append(DICTIONARY[key]['name'])
                    chart_names.append(DICTIONARY[key]['chartName'])
                    identifiers.append(key)
                row[keys[key]] = value
            answer.append(row)
        # sort

        answer = sorted(answer, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
        if len(answer) == 0:
            raise ESQueryResultEmpty()
        return {
            'chartNames': chart_names,
            'header': header,
            'ids': identifiers,
            'rows': answer
        }

    def get(self, request):

        metrics = request.GET.getlist('metrics[]', [])
        dates = get_dates_from_request(request, False)
        response = {}
        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            es_helper = ESResumeStatisticHelper()
            es_query = es_helper.get_data(dates, metrics)
            response['data'] = self.transform_data(es_query)
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class AvailableDays(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def get(self, request):
        es_helper = ESResumeStatisticHelper()
        available_days = es_helper.get_available_days()

        calendar_info = get_calendar_info()
        response = {
            'availableDays': available_days,
            'info': calendar_info
        }

        return JsonResponse(response)
