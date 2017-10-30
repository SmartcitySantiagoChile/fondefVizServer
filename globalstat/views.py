# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.utils import dateparse

from elasticsearch_dsl import Q

from globalstat.esglobalstatichelper import ESGlobalStaticHelper

# to translate variable to user name
DICTIONARY = {
    "date": {"name": "Día", "order": 1},
    "transactionWithoutRoute": {"name": "transacciones sin servicio asignado", "order": 2},
    "transactionWithRoute": {"name": "Transacciones con servicio asignado", "order": 3},
    "transactionNumber": {"name": "Número de transacciones", "order": 4},
    "transactionOnTrainNumber": {"name": "Número de transacciones en metrotren", "order": 5},
    "transactionOnMetroNumber": {"name": "Número de transacciones en metro", "order": 6},
    "transactionOnBusNumber": {"name": "Número de transacciones en bus", "order": 7},
    "transactionOnBusStation": {"name": "Transacciones en zona paga", "order": 8},

    "averageVelocityInAfternoonRushTrips": {"name": "Velocidad prom. de viajes en punta tarde", "order": 9},
    "averageTimeInAfternoonRushTrips": {"name": "Tiempo prom. de viajes en punta tarde", "order": 10},
    "averageDistanceInAfternoonRushTrips": {"name": "Distancia prom. de viajes en punta tarde", "order": 11},
    "tripNumberInAfternoonRushHour": {"name": "Número de viajes en punta tarde", "order": 12},

    "averageVelocityInMorningRushTrips": {"name": "Velocidad prom. de viaje en punta mañana", "order": 13},
    "averageTimeInMorningRushTrips": {"name": "Tiempo prom. de viaje en punta mañana", "order": 14},
    "averageDistanceInMorningRushTrips": {"name": "Distancia prom. de viajes en punta mañana", "order": 15},
    "tripNumberInMorningRushHour": {"name": "Número de viajes en punta mañana", "order": 16},

    "licensePlateNumber": {"name": "Número de patentes", "order": 17},
    "GPSPointsNumber": {"name": "Número de puntos GPS", "order": 18},
    "GPSNumberWithRoute": {"name": "Número de GPS con servicio asignado", "order": 19},
    "GPSNumberWithoutRoute": {"name": "Número de pulsos GPS sin servicio asignado", "order": 20},

    "validTripNumber": {"name": "Número de viajes válido", "order": 21},
    "tripsWithOneStage": {"name": "Número de viajes con una etapa", "order": 22},
    "tripsWithTwoStages": {"name": "Número de viajes con dos etapas", "order": 23},
    "tripsWithThreeStages": {"name": "Número de viajes con tres etapas", "order": 24},
    "tripsWithFourStages": {"name": "Número de viajes con cuatro etapas", "order": 25},
    "tripsWithFiveOrMoreStages": {"name": "Número de viajes con cinco o más etapas", "order": 26},
    "tripsWithOnlyMetro": {"name": "Número de Viajes solo en metro", "order": 27},

    "stagesWithBusAlighting": {"name": "Número de etapas en bus", "order": 28},
    "stagesWithTrainAlighting": {"name": "Número de etapas en metrotren", "order": 29},
    "stagesWithMetroAlighting": {"name": "Número de etapas en metro", "order": 30},

    "expeditionNumber": {"name": "Número de expediciones", "order": 31},
    "maxExpeditionTime": {"name": "Tiempo de expedición máximo", "order": 32},
    "minExpeditionTime": {"name": "Tiempo de expedición mínimo", "order": 33},
    "averageExpeditionTime": {"name": "Tiempo prom. de expedición", "order": 34},

    "smartcardNumber": {"name": "Número de tarjetas", "order": 35},
    "dayType": {"name": "Tipo de día", "order": 36},

    "tripNumber": {"name": "Número de viajes", "order": 37},
    "averageTimeOfTrips": {"name": "Tiempo promedio de viajes", "order": 38},
    "averageVelocityOfTrips": {"name": "Velocidad prom. de viajes", "order": 39},
    "averageTimeBetweenGPSPoints": {"name": "Tiempo prom. entre pulsos GPS", "order": 40},
    "averageDistanceOfTrips": {"name": "Distancia promedio de viajes", "order": 41},

    "tripsThatUseMetro": {"name": "Número de viajes que usan metro", "order": 42},
    "completeTripNumber": {"name": "Número de viajes completo", "order": 43},
    "stagesWithBusStationAlighting": {"name": "Número de etapas con bajada en zona paga", "order": 43},
    "tripsWithoutLastAlighting": {"name": "Número de viajes sin última bajada", "order": 44}
}


class Resume(View):
    """  """

    def __init__(self):
        """ Constructor """
        super(Resume, self).__init__()
        self.es_helper = ESGlobalStaticHelper()

        self.context = {}
        self.context.update(self.es_helper.get_form_data())

        attributes = []
        for key, value in DICTIONARY.items():
            attributes.append({"value": key, "item": value["name"]})

        self.context["metrics"] = attributes

    def get(self, request):
        template = "globalstat/resume.html"

        return render(request, template, self.context)


class Detail(View):
    """  """

    def __init__(self):
        super(Detail, self).__init__()
        self.es_helper = ESGlobalStaticHelper()

        self.context = {}
        self.context.update(self.es_helper.get_form_data())

        attributes = []
        for key, value in DICTIONARY.items():
            attributes.append({"value": key, "item": value["name"]})

        self.context["metrics"] = attributes

    def get(self, request):
        template = "globalstat/detail.html"

        return render(request, template, self.context)


class Data(View):
    """ """

    def __init__(self):
        super(Data, self).__init__()
        self.es_helper = ESGlobalStaticHelper()

    def buildQuery(self, request):
        """ create es-query based on params given by user """

        metrics = request.GET.getlist("metrics[]")
        period = request.GET.getlist("period[]")
        dayType = request.GET.get("dayType")

        esQuery = self.es_helper.get_base_query()

        if len(metrics) == 0:
            metrics = ["transactionWithoutRoute", "transactionWithRoute", "transactionNumber",
                       "transactionOnTrainNumber", "transactionOnMetroNumber", "transactionOnBusNumber",
                       "transactionOnBusStation",

                       "averageVelocityInAfternoonRushTrips", "averageTimeInAfternoonRushTrips"
                       "averageDistanceInAfternoonRushTrips", "tripNumberInAfternoonRushHour",

                       "averageVelocityInMorningRushTrips", "averageTimeInMorningRushTrips",
                       "averageDistanceInMorningRushTrips", "tripNumberInMorningRushHour",

                       "licensePlateNumber", "GPSPointsNumber",
                       "GPSNumberWithRoute", "GPSNumberWithoutRoute",

                       "expeditionNumber", "maxExpeditionTime",
                       "minExpeditionTime", "averageExpeditionTime",

                       "smartcardNumber",

                       "tripNumber", "averageTimeOfTrips", "averageVelocityOfTrips",
                       "averageTimeBetweenGPSPoints", "averageDistanceOfTrips",

                       "tripsThatUseMetro",
                       "completeTripNumber",
                       "stagesWithBusStationAlighting",
                       "tripsWithoutLastAlighting"
                                               
                       "validTripNumber",
                       "tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages",
                       "tripsWithFourStages", "tripsWithFiveOrMoreStages",
                       "tripsWithOnlyMetro",

                       "stagesWithBusAlighting",
                       "stagesWithTrainAlighting",
                       "stagesWithMetroAlighting",
                       ]

        esQuery = esQuery.source(["date"] + metrics)

        if dayType is not None:
            esQuery = esQuery.filter('term', dayType=dayType)

        timeRanges = None
        for date in period:
            timeRange = Q("range", date={
                "gte": date,
                "lte": date,
                "format": "YYYY-MM-dd"
            })
            if timeRanges is None:
                timeRanges = timeRange
            else:
                timeRanges = timeRanges | timeRange

        if timeRanges is not None:
            esQuery = esQuery.query(timeRanges)

        return esQuery

    def transformESAnswer(self, esQuery):
        """ transform ES answer to something util to web client """
        keys = {
            "date": 0
        }
        header = [DICTIONARY["date"]["name"]]
        answer = []

        for hit in esQuery.scan():
            hitRow = hit.to_dict()
            row = list(range(len(hitRow.keys())))
            for key, value in hitRow.iteritems():
                if not key in keys.keys():
                    keys[key] = len(header)
                    header.append(DICTIONARY[key]["name"])
                row[keys[key]] = value
            answer.append(row)
        # sort
        answer = sorted(answer, key=lambda x: dateparse.parse_datetime(x[0]))

        return {
            "header": header,
            "rows": answer
        }

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
