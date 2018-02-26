# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.models import TimePeriod
from localinfo.helper import PermissionBuilder

from esapi.helper.speed import ESSpeedHelper


class MatrixHTML(View):

    def get(self, request):
        template = "speed/matrix.html"
        es_helper = ESSpeedHelper()
        context = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        return render(request, template, context)


class RankingHTML(View):

    def get(self, request):
        template = "speed/ranking.html"
        es_helper = ESSpeedHelper()
        context = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        return render(request, template, context)


class SpeedVariationHTML(View):

    def get(self, request):
        template = "speed/variation.html"

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        es_helper = ESSpeedHelper()

        context = {
            'dayTypes': TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True),
            'routes': es_helper.get_route_list(valid_operator_list)
        }

        return render(request, template, context)
