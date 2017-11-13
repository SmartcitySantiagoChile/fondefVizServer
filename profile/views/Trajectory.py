# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import View

from localinfo.models import HalfHour
from profile.esprofilehelper import ESProfileHelper


class TrajectoryView(View):
    def __init__(self):
        super(TrajectoryView, self).__init__()

        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()
        self.base_params["routes"] = self.es_helper.get_unique_list_query("route", size=1000)
        self.base_params = self.es_helper.make_multisearch_query_for_aggs(self.base_params)

    def get(self, request):
        template = "profile/trajectory.html"

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)
        context = self.base_params
        context['minutes'] = minutes

        return render(request, template, context)
