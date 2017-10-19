# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from collections import defaultdict

from elasticsearch_dsl import Search


class Show(View):
    """  """

    def __init__(self):
        """ Constructor """
        super(Show, self).__init__()
        self.context = {}
        
    def get(self, request):
        template = "globalstat/show.html"

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
                data[key].append(value)

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
