# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from esapi.helper.profile import ESProfileHelper

from localinfo.models import HalfHour


class LoadProfileByExpeditionView(View):

    def get(self, request):
        template = "profile/byExpedition.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]

        es_helper = ESProfileHelper()
        base_params = es_helper.get_base_params()

        context = {
            'data_filter': es_helper.make_multisearch_query_for_aggs(base_params)
        }
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)
