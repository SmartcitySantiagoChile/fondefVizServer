# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

from elasticsearch_dsl import Search

# elastic search index name
INDEX_NAME = "shape"


class Route(View):
    ''' get polyline of route '''

    def __init__(self):
        ''' contructor '''
        super(View, self).__init__()

    def get(self, request):
        route = request.GET.get("route")

        client = settings.ES_CLIENT
        routeQuery = Search(using=client, index=INDEX_NAME)
        routeQuery = routeQuery.filter("term", route=route)
        routeQuery = routeQuery.source(["points"])

        points = []
        for hit in routeQuery.scan():
            data = hit.to_dict()
            for point in data["points"]:
                points.append({
                    "latitude": point["latitude"],
                    "longitude": point["longitude"]
                })

        response = {
            "points": points
        }

        return JsonResponse(response, safe=True)


class Map(View):
    ''' load html map to show route polyline '''

    def __init__(self):
        ''' contructor '''
        super(View, self).__init__()

        client = settings.ES_CLIENT
        routeQuery = Search(using=client, index=INDEX_NAME)
        routeQuery = routeQuery.source(["route"])

        routes = []
        for hit in routeQuery.scan():
            data = hit.to_dict()
            routes.append(data["route"])

        self.context = {
            "routes": routes
        }

    def get(self, request):
        template = "shape/map.html"

        return render(request, template, self.context)
