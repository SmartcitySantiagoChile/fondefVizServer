# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from collections import defaultdict

from models import DataSourcePath, DataSourceFile

import os
import re

class LoadData(View):
    """ Load data to elastic search """

    def __init__(self):
        self.context = {}

    def post(self):
        """  """


class DeleteData(View):
    """ Delete data to elastic search """

    def __init__(self):
        self.context = {}

    def post(self):
        """  """


class LoadManager(View):
    ''' load  web page to load files '''

    def __init__(self):
        ''' contructor '''
        self.context={}

    def get(self, request):
        template = "datamanager/loadManager.html"

        # define the order table appear in web page
        tables = [
            {
                "bubble_title": "", "bubble_content": u"Archivo que relaciona el nombre de los servicios conocidos por los usuarios y los asignados por Sonda.",
                "id": "routeDictTable", "title_icon": "fa-map-o", "title": "Diccionario de servicios"
            },
            {
                "bubble_title": "", "bubble_content": u"Descripcion de caracteristicas generales",
                "id": "generalTable", "title_icon": "", "title": "Datos generales"
            },
            {
                "bubble_title": "", "bubble_content": u"Archivos de viajes",
                "id": "travelTable", "title_icon": "", "title": "Viajes"
            },
            {
                "bubble_title": "", "bubble_content": u"Archivos de velocidades",
                "id": "speedTable", "title_icon": "", "title": "Velocidades"
            },
            {
                "bubble_title": "", "bubble_content": u"Archivo con geometría de servicios",
                "id": "shapeTable", "title_icon": "", "title": "Geometria de servicios"
            },
            {
                "bubble_title": "", "bubble_content": u"Archivo con secuencia de paradas por servicio",
                "id": "stopSequenceTable", "title_icon": "", "title": "Secuencia de paradas"
            },
            {
                "bubble_title": "", "bubble_content": u"Archivo de perfiles de carga",
                "id": "profileTable", "title_icon": "", "title": "Perfiles"
            }
        ]
        self.context['tables'] = tables

        return render(request, template, self.context)


class getLoadFileData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def getRouteDictFileList(self):
        """ list all files in directory with code """
        fileDict = defaultdict(list)

        dataSourcePath = DataSourcePath.objects.all()
        for dataSource in dataSourcePath:
            path = dataSource.path
            # if is running on windows
            if os.name == "nt":
                path = os.path.join(settings.BASE_DIR, "media")

            pattern = re.compile("." + dataSource.filePattern)
            fileNameList = filter(lambda fileName: pattern.match(fileName), os.listdir(path))
            for fileName in fileNameList:
                fileObj, created = DataSourceFile.objects.get_or_create(fileName=fileName, defaults={
                    "dataSourcePath": path, "discoverAt": timezone.now()})
                if created:
                    i = 0
                    with open(os.path.join(path, fileName)) as f:
                        for i, _ in enumerate(f):
                            pass
                    fileObj.lines = i + 1
                    fileObj.save()
                fileDict[dataSource.code].append(fileObj.getDict())

        return fileDict

    def get(self, request):
        ''' expedition data '''
        response = {}
        response['routeDictFiles'] = self.getRouteDictFileList()

        return JsonResponse(response, safe=False)