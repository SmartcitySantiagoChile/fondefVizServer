# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import PermissionBuilder, get_day_type_list_for_select_input

from esapi.helper.speed import ESSpeedHelper


class MatrixHTML(View):

    def get(self, request):
        template = "speed/matrix.html"
        context = {
            'day_types': get_day_type_list_for_select_input()
        }

        return render(request, template, context)


class RankingHTML(View):

    def get(self, request):
        template = "speed/ranking.html"
        context = {
            'day_types': get_day_type_list_for_select_input()
        }

        return render(request, template, context)


class SpeedVariationHTML(View):

    def get(self, request):
        template = "speed/variation.html"

        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        es_helper = ESSpeedHelper()

        context = {
            'day_types': get_day_type_list_for_select_input(),
            'routes': es_helper.get_route_list(valid_operator_list)
        }

        return render(request, template, context)
