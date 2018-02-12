# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from esapi.helper.speed import ESSpeedHelper


class RankingHTML(View):

    def get(self, request):
        template = "speed/ranking.html"
        es_helper = ESSpeedHelper()
        context = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        return render(request, template, context)
