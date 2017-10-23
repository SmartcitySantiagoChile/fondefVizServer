# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from collections import defaultdict

from elasticsearch_dsl import Search

# to translate variable to user name
DICTIONARY = {
    "date": "Día",
    "transactionWithoutRoute": "transacciones sin servicio asignado",
    "transactionWithRoute": "Transacciones con servicio asignado",
    "transactionNumber": "Número de transacciones",
    "transactionOnTrainNumber": "Número de transacciones en metrotren",
    "transactionOnMetroNumber": "Número de transacciones en metro",
    "transactionOnBusNumber": "Número de transacciones en bus",
    "transactionOnBusStation": "Transacciones en zona paga",

    "averageVelocityInAfternoonRushTrips": "Velocidad prom. de viajes en punta tarde",
    "averageTimeInAfternoonRushTrips": "Tiempo prom. de viajes en punta tarde",
    "averageDistanceInAfternoonRushTrips": "Distancia prom. de viajes en punta tarde",

    "averageVelocityInMorningRushTrips": "Velocidad prom. de viaje en punta mañana",
    "averageTimeInMorningRushTrips": "Tiempo prom. de viaje en punta mañana",
    "averageDistanceInMorningRushTrips": "Distancia prom. de viajes en punta mañana",

    "licensePlateNumber": "Número de patentes",
    "GPSPointsNumber": "Número de puntos GPS",
    "GPSNumberWithRoute": "Número de GPS con servicio asignado",
    "GPSNumberWithoutRoute": "Número de pulsos GPS sin servicio asignado",

    "validTripNumber": "Número de viajes válido",
    "tripsWithOneStage": "Número de viajes con una etapa",
    "tripsWithTwoStages": "Número de viajes con dos etapas",
    "tripsWithThreeStages": "Número de viajes con tres etapas",
    "tripsWithFourStages": "Número de viajes con cuatro etapas",
    "tripsWithFiveOrMoreStages": "Número de viajes con cinco o más etapas",
    "tripsWithOnlyMetro": "Número de Viajes solo en metro",
    "stagesWithBusAlighting": "Número de etapas en bus",
    "stagesWithTrainAlighting": "Número de etapas en metrotren",
    "stagesWithMetroAlighting": "Número de etapas en metro",

    "expeditionNumber": "Número de expediciones",
    "maxExpeditionTime": "Tiempo de expedición máximo",
    "minExpeditionTime": "Tiempo de expedición mínimo",
    "averageExpeditionTime": "Tiempo prom. de expedición",

    "tripNumberInAfternoonRushHour": "Número de viajes en punta tarde",
    "smartcardNumber": "Número de tarjetas",
    "dayType": "Tipo de día",

    "tripNumber": "Número de viajes",
    "averageTimeOfTrips": "Tiempo promedio de viajes",
    "averageVelocityOfTrips": "Velocidad prom. de viajes",
    "averageTimeBetweenGPSPoints": "Tiempo prom. entre pulsos GPS",
    "averageDistanceOfTrips": "Distancia promedio de viajes",
    "tripNumberInMorningRushHour": "Número de viajes en punta mañana",

    "tripsThatUseMetro": "Número de viajes que usan metro",
    "completeTripNumber": "Número de viajes completo",
    "stagesWithBusStationAlighting": "Número de etapas con bajada en zona paga",
    "tripsWithoutLastAlighting": "Número de viajes sin última bajada"
}


class Show(View):
    """  """

    def __init__(self):
        """ Constructor """
        super(Show, self).__init__()
        self.context = {}

    def get(self, request):
        template = "globalstat/show.html"

        return render(request, template, self.context)


class Detail(View):
    """  """

    def __init__(self):
        """ Constructor """
        super(Detail, self).__init__()
        self.context = {}

    def get(self, request):
        template = "globalstat/detail.html"

        return render(request, template, self.context)


class Data(View):
    """ """

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        # get list of profile*
        client = settings.ES_CLIENT
        INDEX_NAME = "general"
        esQuery = Search(using=client, index=INDEX_NAME)

        esQuery = esQuery.source(["date", "averageVelocityInAfternoonRushTrips", "transactionWithoutRoute",
                                  "averageTimeInMorningRushTrips", "minExpeditionTime", "licensePlateNumber",
                                  "averageVelocityInMorningRushTrips", "averageTimeInAfternoonRushTrips",
                                  "GPSNumberWithRoute", "stagesWithMetroAlighting", "tripsWithTwoStages",
                                  "averageDistanceInAfternoonRushTrips", "maxExpeditionTime", "transactionWithRoute",
                                  "tripNumberInAfternoonRushHour", "smartcardNumber", "tripsWithOnlyMetro", "dayType",
                                  "tripsWithOneStage", "stagesWithBusAlighting", "averageExpeditionTime",
                                  "GPSPointsNumber", "transactionOnTrainNumber", "averageDistanceInMorningRushTrips",
                                  "stagesWithTrainAlighting", "tripsWithFourStages", "expeditionNumber",
                                  "tripsWithThreeStages", "averageTimeOfTrips", "tripsWithFiveOrMoreStages",
                                  "averageVelocityOfTrips", "averageTimeBetweenGPSPoints", "averageDistanceOfTrips",
                                  "tripNumber", "transactionOnMetroNumber", "validTripNumber", "transactionOnBusNumber",
                                  "tripNumberInMorningRushHour", "transactionNumber", "tripsThatUseMetro",
                                  "completeTripNumber", "GPSNumberWithoutRoute", "stagesWithBusStationAlighting",
                                  "transactionOnBusStation", "tripsWithoutLastAlighting"])
        esQuery = esQuery.sort("date")

        return esQuery

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        data = defaultdict(list)

        for hit in esQuery.scan():
            record = hit.to_dict()

            for key, value in record.iteritems():
                data[DICTIONARY[key]].append(value)

        return data

    def get(self, request):
        """ expedition data """
        response = {}

        esQuery = self.buildQuery(request)
        response['data'] = self.transformESAnswer(esQuery)
        # debug
        # response['query'] = esQuery.to_dict()
        # return JsonResponse(response, safe=False)
        # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}

        return JsonResponse(response, safe=False)
