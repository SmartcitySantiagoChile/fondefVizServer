from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

from elasticsearch_dsl import Search, Q, A, MultiSearch
from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty

from models import DataSourcePath

# elastic search index name 
INDEX_NAME="profiles"
# elastic search fields
DAY_TYPE = 'TipoDia'
ROUTE = 'ServicioSentido'
TIME_PERIOD = 'PeriodoTSExpedicion'


class LoadManager(View):
    ''' load  web page to load files '''

    def __init__(self):
        ''' contructor '''
        self.context={}

    def get(self, request):
        template = "datamanager/loadManager.html"

        return render(request, template, self.context)


class getLoadFileData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def getRouteDictFileList(self):
        """ list all files in directory with code """
        dataSourcePath = DataSourcePath.objects.get(code="routeDict")
        path = dataSourcePath.path
        filePattern = dataSourcePath.patternFile

        from django.conf import settings
        import os

        path = os.path.join(settings.BASE_DIR, "media")

    def get(self, request):
        ''' expedition data '''
        response = {}
        response['routeDictFiles'] = self.getRouteDictFileList()

        return JsonResponse(response, safe=False)


