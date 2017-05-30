from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, A, MultiSearch


class LoadProfileGeneric(View):
    ''' generic view to load profile data'''

    # elastic search index name 
    INDEX_NAME="profiles"

    def __init__(self):
        ''' contructor '''
        self.context={}

        routes, dayTypes, timePeriods = self.getParamsList()
        self.context['dayTypes'] = dayTypes
        self.context['periods'] = timePeriods
        self.context['routes'] = routes

    def getParamsList(self):
        ''' retrieve all routes availables in elasticsearch'''
        client = settings.ES_CLIENT

        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "ServicioSentido", size=1000)
        esRouteQuery.aggs.bucket('unique_routes', aggs)

        esDayTypeQuery = Search()
        esDayTypeQuery = esDayTypeQuery[:0]
        aggs = A('terms', field = "TipoDia", size=10)
        esDayTypeQuery.aggs.bucket('unique_day_types', aggs)

        esTimePeriodQuery = Search()
        esTimePeriodQuery = esDayTypeQuery[:0]
        aggs = A('terms', field = "PeriodoTSExpedicion", size=50)
        esTimePeriodQuery.aggs.bucket('unique_time_periods', aggs)
  
        multiSearch = MultiSearch(using=client, index=self.INDEX_NAME)
        multiSearch = multiSearch.add(esRouteQuery).add(esDayTypeQuery).add(esTimePeriodQuery)

        # to see the query generated
        #print multiSearch.to_dict()
        responses = multiSearch.execute()

        routes = []
        for tag in responses[0].aggregations.unique_routes.buckets:
            routes.append(tag.key)
        routes.sort()

        dayTypes = []
        for tag in responses[1].aggregations.unique_day_types.buckets:
            dayTypes.append(tag.key)
        dayTypes.sort()

        timePeriods = []
        for tag in responses[2].aggregations.unique_time_periods.buckets:
            timePeriods.append(tag.key)
        timePeriods.sort()

        return routes, dayTypes, timePeriods




