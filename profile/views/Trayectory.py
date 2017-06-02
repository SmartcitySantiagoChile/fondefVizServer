from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A, MultiSearch
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from LoadProfileGeneric import LoadProfileGeneric

class TrayectoryView(LoadProfileGeneric):
    ''' '''

    def __init__(self):
        ''' contructor '''

        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "ServicioSentido", size=1000)
        esRouteQuery.aggs.bucket('unique', aggs)
 
        esQueryDict = {}
        esQueryDict['routes'] = esRouteQuery
        
        super(TrayectoryView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/trayectory.html"

        return render(request, template, self.context)

