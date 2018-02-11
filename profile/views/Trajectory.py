# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.models import HalfHour
from esapi.helper.profile import ESProfileHelper


class TrajectoryView(View):

    def get(self, request):
        template = "profile/trajectory.html"

        es_helper = ESProfileHelper()
        base_params = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]
        context = base_params
        context['minutes'] = minutes

        return render(request, template, context)
