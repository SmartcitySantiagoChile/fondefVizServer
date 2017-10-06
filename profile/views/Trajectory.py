# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

from elasticsearch_dsl import Search, A
from LoadProfileGeneric import LoadProfileGeneric

from localinfo.models import HalfHour


class TrajectoryView(LoadProfileGeneric):
    """  """

    def __init__(self):
        esRouteQuery = Search()
        esRouteQuery = esRouteQuery[:0]
        aggs = A('terms', field = "route", size=1000)
        esRouteQuery.aggs.bucket('unique', aggs)

        esQueryDict = {}
        esQueryDict['routes'] = esRouteQuery
        
        super(TrajectoryView, self).__init__(esQueryDict)

    def get(self, request):
        template = "profile/trajectory.html"

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)
        self.context['minutes'] = minutes

        return render(request, template, self.context)
