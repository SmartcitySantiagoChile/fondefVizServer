# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.models import HalfHour
from esapi.helper.profile import ESProfileHelper


class LoadProfileByStopView(View):
    def __init__(self):
        super(LoadProfileByStopView, self).__init__()
        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/byStop.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]
        context = {
            'data_filter': self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        }
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)
