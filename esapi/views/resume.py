# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.http import JsonResponse
from django.utils import dateparse
from django.contrib.auth.mixins import PermissionRequiredMixin

from esapi.helper.resume import ESResumeStatisticHelper
from esapi.errors import ESQueryResultEmpty

# to translate variable to user name
DICTIONARY = {
    'date': {'name': 'Día', 'order': 1},
    'transactionWithoutRoute':
        {'name': 'transacciones sin servicio asignado',
         'chartName': 'Sin servicio asignado',
         'order': 2},
    'transactionWithRoute':
        {'name': 'Transacciones con servicio asignado',
         'chartName': 'Con servicio asignado',
         'order': 3},
    'transactionNumber':
        {'name': 'Número de transacciones', 'chartName': '', 'order': 4},
    'transactionOnTrainNumber':
        {'name': 'Número de transacciones en metrotren', 'chartName': 'Metrotren', 'order': 5},
    'transactionOnMetroNumber':
        {'name': 'Número de transacciones en metro', 'chartName': 'Metro', 'order': 6},
    'transactionOnBusNumber':
        {'name': 'Número de transacciones en bus', 'chartName': 'Bus', 'order': 7},
    'transactionOnBusStation':
        {'name': 'Transacciones en zona paga', 'chartName': 'Zona paga', 'order': 8},

    'averageVelocityInAfternoonRushTrips':
        {'name': 'Velocidad prom. de viajes en punta tarde (Km/H)', 'chartName': '', 'order': 9},
    'averageTimeInAfternoonRushTrips':
        {'name': 'Tiempo prom. de viajes en punta tarde', 'chartName': '', 'order': 10},
    'averageDistanceInAfternoonRushTrips':
        {'name': 'Distancia prom. de viajes en punta tarde (mts)', 'chartName': '', 'order': 11},
    'tripNumberInAfternoonRushHour':
        {'name': 'Número de viajes en punta tarde', 'chartName': '', 'order': 12},

    'averageVelocityInMorningRushTrips':
        {'name': 'Velocidad prom. de viaje en punta mañana (Km/H)', 'chartName': '', 'order': 13},
    'averageTimeInMorningRushTrips':
        {'name': 'Tiempo prom. de viaje en punta mañana', 'chartName': '', 'order': 14},
    'averageDistanceInMorningRushTrips':
        {'name': 'Distancia prom. de viajes en punta mañana (mts)', 'chartName': '', 'order': 15},
    'tripNumberInMorningRushHour':
        {'name': 'Número de viajes en punta mañana', 'chartName': '', 'order': 16},

    'licensePlateNumber':
        {'name': 'Número de patentes', 'chartName': '', 'order': 17},
    'GPSPointsNumber':
        {'name': 'Número de pulsos GPS', 'chartName': '', 'order': 18},
    'GPSNumberWithRoute':
        {'name': 'Número de GPS con servicio asignado', 'chartName': '', 'order': 19},
    'GPSNumberWithoutRoute':
        {'name': 'Número de pulsos GPS sin servicio asignado', 'chartName': '', 'order': 20},
    'averageTimeBetweenGPSPoints':
        {'name': 'Tiempo prom. entre pulsos GPS', 'chartName': '', 'order': 40},

    'validTripNumber':
        {'name': 'Número de viajes expandido', 'chartName': '', 'order': 21},
    'tripsWithOneStage':
        {'name': 'Número de viajes con una etapa', 'chartName': '1 etapa', 'order': 22},
    'tripsWithTwoStages':
        {'name': 'Número de viajes con dos etapas', 'chartName': '2 etapas', 'order': 23},
    'tripsWithThreeStages':
        {'name': 'Número de viajes con tres etapas', 'chartName': '3 etapas', 'order': 24},
    'tripsWithFourStages':
        {'name': 'Número de viajes con cuatro etapas', 'chartName': '4 etapas', 'order': 25},
    'tripsWithFiveOrMoreStages':
        {'name': 'Número de viajes con cinco o más etapas', 'chartName': '5 o más etapas', 'order': 26},
    'tripsWithOnlyMetro':
        {'name': 'Número de Viajes solo en metro', 'chartName': '', 'order': 27},

    'stagesWithBusAlighting':
        {'name': 'Número de etapas en bus', 'chartName': 'Bus', 'order': 28},
    'stagesWithTrainAlighting':
        {'name': 'Número de etapas en metrotren', 'chartName': 'Metrotren', 'order': 29},
    'stagesWithMetroAlighting':
        {'name': 'Número de etapas en metro', 'chartName': 'Metro', 'order': 30},
    'stagesWithBusStationAlighting':
        {'name': 'Número de etapas con bajada en zona paga', 'chartName': 'Zona paga', 'order': 45},

    'expeditionNumber':
        {'name': 'Número de expediciones', 'chartName': '', 'order': 31},
    'maxExpeditionTime':
        {'name': 'Tiempo de expedición máximo', 'chartName': '', 'order': 32},
    'minExpeditionTime':
        {'name': 'Tiempo de expedición mínimo', 'chartName': '', 'order': 33},
    'averageExpeditionTime':
        {'name': 'Tiempo prom. de expedición', 'chartName': '', 'order': 34},

    'smartcardNumber':
        {'name': 'Número de tarjetas', 'chartName': '', 'order': 35},
    'dayType':
        {'name': 'Tipo de día', 'chartName': '', 'order': 36},

    'tripNumber':
        {'name': 'Número de viajes válido', 'chartName': '', 'order': 37},
    'averageTimeOfTrips':
        {'name': 'Tiempo promedio de viajes', 'chartName': '', 'order': 38},
    'averageVelocityOfTrips':
        {'name': 'Velocidad prom. de viajes (Km/H)', 'chartName': '', 'order': 39},
    'averageDistanceOfTrips':
        {'name': 'Distancia promedio de viajes (mts)', 'chartName': '', 'order': 41},

    'tripsThatUseMetro':
        {'name': 'Número de viajes que usan metro', 'chartName': '', 'order': 42},
    'completeTripNumber':
        {'name': 'Número de viajes completo', 'chartName': '', 'order': 43},
    'tripsWithoutLastAlighting':
        {'name': 'Número de viajes sin última bajada', 'chartName': '', 'order': 44}
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
            row = list(range(len(hit_row.keys())))
            for key, value in hit_row.iteritems():
                if key not in keys.keys():
                    keys[key] = len(header)
                    header.append(DICTIONARY[key]['name'])
                    chart_names.append(DICTIONARY[key]['chartName'])
                    identifiers.append(key)
                row[keys[key]] = value
            answer.append(row)
        # sort
        answer = sorted(answer, key=lambda x: dateparse.parse_datetime(x[0]))

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
        start_date = request.GET.get('startDate')[:10]
        end_date = request.GET.get('endDate', '')[:10]

        if start_date and not end_date:
            end_date = start_date

        response = {}
        try:
            es_helper = ESResumeStatisticHelper()
            es_query = es_helper.ask_for_data(start_date, end_date, metrics)

            response['data'] = self.transform_data(es_query)
        except ESQueryResultEmpty as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class AvailableDays(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def get(self, request):
        es_helper = ESResumeStatisticHelper()
        available_days = es_helper.ask_for_available_days()

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)
