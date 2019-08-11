# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_day_type_list_for_select_input


class IndexHTML(View):

    def get(self, request):
        template = "busstationdistribution/index.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input()
            },
            'tabs': {
                'header': ['Gráfico', 'Mapa'],
                'content': ['<div id="barChart" style="height:600px;"></div>',
                            '<div id="mapid" style="height: 500px;min-height: 500px"></div>']
            }
        }

        return render(request, template, context)
