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
    "transactionWithoutRoute":
        {"name": "transacciones sin servicio asignado",
         "chartName": "Sin servicio asignado",
         "order": 2},
    "transactionWithRoute":
        {"name": "Transacciones con servicio asignado",
         "chartName": "Con servicio asignado",
         "order": 3},
    "transactionNumber":
        {"name": "Número de transacciones", "chartName": "", "order": 4},
    "transactionOnTrainNumber":
        {"name": "Número de transacciones en metrotren", "chartName": "Metrotren", "order": 5},
    "transactionOnMetroNumber":
        {"name": "Número de transacciones en metro", "chartName": "Metro", "order": 6},
    "transactionOnBusNumber":
        {"name": "Número de transacciones en bus", "chartName": "Bus", "order": 7},
    "transactionOnBusStation":
        {"name": "Transacciones en zona paga", "chartName": "Zona paga", "order": 8},

    "averageVelocityInAfternoonRushTrips":
        {"name": "Velocidad prom. de viajes en punta tarde (Km/H)", "chartName": "", "order": 9},
    "averageTimeInAfternoonRushTrips":
        {"name": "Tiempo prom. de viajes en punta tarde", "chartName": "", "order": 10},
    "averageDistanceInAfternoonRushTrips":
        {"name": "Distancia prom. de viajes en punta tarde (mts)", "chartName": "", "order": 11},
    "tripNumberInAfternoonRushHour":
        {"name": "Número de viajes en punta tarde", "chartName": "", "order": 12},

    "averageVelocityInMorningRushTrips":
        {"name": "Velocidad prom. de viaje en punta mañana (Km/H)", "chartName": "", "order": 13},
    "averageTimeInMorningRushTrips":
        {"name": "Tiempo prom. de viaje en punta mañana", "chartName": "", "order": 14},
    "averageDistanceInMorningRushTrips":
        {"name": "Distancia prom. de viajes en punta mañana (mts)", "chartName": "", "order": 15},
    "tripNumberInMorningRushHour":
        {"name": "Número de viajes en punta mañana", "chartName": "", "order": 16},

    "licensePlateNumber":
        {"name": "Número de patentes", "chartName": "", "order": 17},
    "GPSPointsNumber":
        {"name": "Número de pulsos GPS", "chartName": "", "order": 18},
    "GPSNumberWithRoute":
        {"name": "Número de GPS con servicio asignado", "chartName": "", "order": 19},
    "GPSNumberWithoutRoute":
        {"name": "Número de pulsos GPS sin servicio asignado", "chartName": "", "order": 20},
    "averageTimeBetweenGPSPoints":
        {"name": "Tiempo prom. entre pulsos GPS", "chartName": "", "order": 40},

    "validTripNumber":
        {"name": "Número de viajes expandido", "chartName": "", "order": 21},
    "tripsWithOneStage":
        {"name": "Número de viajes con una etapa", "chartName": "1 etapa", "order": 22},
    "tripsWithTwoStages":
        {"name": "Número de viajes con dos etapas", "chartName": "2 etapas", "order": 23},
    "tripsWithThreeStages":
        {"name": "Número de viajes con tres etapas", "chartName": "3 etapas", "order": 24},
    "tripsWithFourStages":
        {"name": "Número de viajes con cuatro etapas", "chartName": "4 etapas", "order": 25},
    "tripsWithFiveOrMoreStages":
        {"name": "Número de viajes con cinco o más etapas", "chartName": "5 o más etapas", "order": 26},
    "tripsWithOnlyMetro":
        {"name": "Número de Viajes solo en metro", "chartName": "", "order": 27},

    "stagesWithBusAlighting":
        {"name": "Número de etapas en bus", "chartName": "Bus", "order": 28},
    "stagesWithTrainAlighting":
        {"name": "Número de etapas en metrotren", "chartName": "Metrotren", "order": 29},
    "stagesWithMetroAlighting":
        {"name": "Número de etapas en metro", "chartName": "Metro", "order": 30},
    "stagesWithBusStationAlighting":
        {"name": "Número de etapas con bajada en zona paga", "chartName": "Zona paga", "order": 45},

    "expeditionNumber":
        {"name": "Número de expediciones", "chartName": "", "order": 31},
    "maxExpeditionTime":
        {"name": "Tiempo de expedición máximo", "chartName": "", "order": 32},
    "minExpeditionTime":
        {"name": "Tiempo de expedición mínimo", "chartName": "", "order": 33},
    "averageExpeditionTime":
        {"name": "Tiempo prom. de expedición", "chartName": "", "order": 34},

    "smartcardNumber":
        {"name": "Número de tarjetas", "chartName": "", "order": 35},
    "dayType":
        {"name": "Tipo de día", "chartName": "", "order": 36},

    "tripNumber":
        {"name": "Número de viajes válido", "chartName": "", "order": 37},
    "averageTimeOfTrips":
        {"name": "Tiempo promedio de viajes", "chartName": "", "order": 38},
    "averageVelocityOfTrips":
        {"name": "Velocidad prom. de viajes (Km/H)", "chartName": "", "order": 39},
    "averageDistanceOfTrips":
        {"name": "Distancia promedio de viajes (mts)", "chartName": "", "order": 41},

    "tripsThatUseMetro":
        {"name": "Número de viajes que usan metro", "chartName": "", "order": 42},
    "completeTripNumber":
        {"name": "Número de viajes completo", "chartName": "", "order": 43},
    "tripsWithoutLastAlighting":
        {"name": "Número de viajes sin última bajada", "chartName": "", "order": 44}
}


class Resume(View):
    """  """

    def __init__(self):
        """ Constructor """
        super(Resume, self).__init__()

        self.context = {}

        attributes = []
        for key, value in DICTIONARY.items():
            if key == "dayType":
                continue
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
            if key == "dayType":
                continue
            attributes.append({"value": key, "item": value["name"]})

        self.context["metrics"] = attributes

        self.context["tiles_1"] = [
            {"title": DICTIONARY["dayType"]["name"], "title_icon": "fa-calendar", "value": "",
             "value_id": "dayType", "sub_value_id": "date", "sub_title": ""},
            {"title": DICTIONARY["smartcardNumber"]["name"], "title_icon": "fa-credit-card", "value": "",
             "value_id": "smartcardNumber", "sub_value_id": "", "sub_title": ""},
            {"title": DICTIONARY["transactionNumber"]["name"], "title_icon": "fa-group", "value": "",
             "value_id": "transactionNumber", "sub_value_id": "", "sub_title": ""},
        ]

        self.context["tiles_2"] = [
            {"title": DICTIONARY["tripNumber"]["name"], "title_icon": "fa-rocket", "value": "",
             "value_id": "tripNumber", "sub_value_id": "", "sub_title": ""},
            {"title": DICTIONARY["validTripNumber"]["name"], "title_icon": "fa-rocket", "value": "",
             "value_id": "validTripNumber", "sub_value_id": "", "sub_title": ""},
            #{"title": DICTIONARY["completeTripNumber"]["name"], "title_icon": "fa-group", "value": "",
            # "value_id": "completeTripNumber", "sub_value_id": "", "sub_title": ""},
        ]

        self.context["tiles_22"] = [
            {"title": DICTIONARY["tripsThatUseMetro"]["name"], "title_icon": "fa-rocket", "value": "",
             "value_id": "tripsThatUseMetro", "sub_value_id": "validTripNumber", "sub_title": ""},
            {"title": DICTIONARY["tripsWithOnlyMetro"]["name"], "title_icon": "fa-train", "value": "",
             "value_id": "tripsWithOnlyMetro", "sub_value_id": "", "sub_title": ""},
            {"title": DICTIONARY["tripsWithoutLastAlighting"]["name"], "title_icon": "fa-globe", "value": "",
             "value_id": "tripsWithoutLastAlighting", "sub_value_id": "", "sub_title": ""},
        ]
        self.context["tiles_3"] = [
            {"title": DICTIONARY["expeditionNumber"]["name"], "title_icon": "fa-truck", "value": "",
             "value_id": "expeditionNumber", "sub_value_id": "date", "sub_title": ""},
            {"title": DICTIONARY["averageExpeditionTime"]["name"], "title_icon": "fa-repeat", "value": "",
             "value_id": "averageExpeditionTime", "sub_value_id": "", "sub_title": "Minutos"},
            {"title": DICTIONARY["minExpeditionTime"]["name"], "title_icon": "fa-repeat", "value": "",
             "value_id": "minExpeditionTime", "sub_value_id": "", "sub_title": "Minutos"},
            {"title": DICTIONARY["maxExpeditionTime"]["name"], "title_icon": "fa-repeat", "value": "",
             "value_id": "maxExpeditionTime", "sub_value_id": "validTripNumber", "sub_title": "Minutos"},
            {"title": DICTIONARY["licensePlateNumber"]["name"], "title_icon": "fa-truck", "value": "",
             "value_id": "licensePlateNumber", "sub_value_id": "", "sub_title": ""},
        ]


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

        esQuery = self.es_helper.get_base_query()

        if len(metrics) == 0:
            metrics = ["transactionWithoutRoute", "transactionWithRoute", "transactionNumber",
                       "transactionOnTrainNumber", "transactionOnMetroNumber", "transactionOnBusNumber",
                       "transactionOnBusStation",

                       "averageVelocityInAfternoonRushTrips", "averageTimeInAfternoonRushTrips",
                                                              "averageDistanceInAfternoonRushTrips",
                       "tripNumberInAfternoonRushHour",

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
                       "tripsWithoutLastAlighting",

                       "validTripNumber",
                       "tripsWithOneStage", "tripsWithTwoStages", "tripsWithThreeStages",
                       "tripsWithFourStages", "tripsWithFiveOrMoreStages",
                       "tripsWithOnlyMetro",

                       "stagesWithBusAlighting",
                       "stagesWithTrainAlighting",
                       "stagesWithMetroAlighting",

                       "dayType"
                       ]

        esQuery = esQuery.source(["date"] + metrics)

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
        identifiers = ["date"]
        chart_names = ["Día"]
        answer = []

        for hit in esQuery.scan():
            hitRow = hit.to_dict()
            row = list(range(len(hitRow.keys())))
            for key, value in hitRow.iteritems():
                if not key in keys.keys():
                    keys[key] = len(header)
                    header.append(DICTIONARY[key]["name"])
                    chart_names.append(DICTIONARY[key]["chartName"])
                    identifiers.append(key)
                row[keys[key]] = value
            answer.append(row)
        # sort
        answer = sorted(answer, key=lambda x: dateparse.parse_datetime(x[0]))

        return {
            "chartNames": chart_names,
            "header": header,
            "ids": identifiers,
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
