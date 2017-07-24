from django.shortcuts import render

from elasticsearch_dsl import Search, A
from LoadProfileGeneric import LoadProfileGeneric

class TrayectoryView(LoadProfileGeneric):
    ''' '''

    def __init__(self):
        ''' contructor '''
        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "route", size=1000)
        esRouteQuery.aggs.bucket('unique', aggs)

        esQueryDict = {}
        esQueryDict['routes'] = esRouteQuery
        
        super(TrayectoryView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/trayectory.html"

        return render(request, template, self.context)

