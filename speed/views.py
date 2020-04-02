# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_day_type_list_for_select_input


class MatrixHTML(View):

    def get(self, request):
        template = "speed/matrix.html"
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class RankingHTML(View):

    def get(self, request):
        template = "speed/ranking.html"
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)


class SpeedVariationHTML(View):

    def get(self, request):
        template = "speed/variation.html"
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)
