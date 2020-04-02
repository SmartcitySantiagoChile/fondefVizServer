# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_halfhour_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_day_type_list_for_select_input


class LoadBipByOperatorHTML(View):

    def get(self, request):
        template = "bip/byOperator.html"

        context = {
            'data_filter': {
                'minutes': get_halfhour_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input(),
                'day_types': get_day_type_list_for_select_input()
            },
            'tabs': {
                'header': ['Gráfico', 'Mapa'],
                'content': ['<div id="barChart" style="height:600px;"></div>',
                            '<div id="mapid" style="height: 500px;min-height: 500px"></div>']
            }
        }

        return render(request, template, context)
