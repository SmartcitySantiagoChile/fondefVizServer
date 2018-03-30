# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.mixins import PermissionRequiredMixin

from localinfo.helper import get_timeperiod_list_for_select_input, get_day_type_list_for_select_input, \
    get_halfhour_list_for_select_input

import json


class FromToMapHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.travel'

    def get(self, request):
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input(),
                'minutes': get_halfhour_list_for_select_input()
            },
            'mode_selectors': render_to_string('travel/from_to_mode_selectors.html'),
            'stage_selectors': render_to_string('travel/from_to_stage_selectors.html'),
        }
        return render(request, "travel/from_to.html", context)


class LargeTravelsHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.travel'

    def get(self, request):
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input()
            },
            'selectors': render_to_string('travel/large_selectors.html')
        }

        return render(request, 'travel/large.html', context)


class MapHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.travel'

    def get(self, request):
        # TODO: remove sector dictionary when js files were refactored
        # zonas 777 para cada sector
        sectors = dict()
        sectors['Lo Barnechea'] = [202, 642]
        sectors['Centro'] = [267, 276, 285, 286]
        sectors['Providencia'] = [175, 176, 179]
        sectors['Las Condes'] = [207, 215, 216]
        sectors['Vitacura'] = [191, 192, 193, 195, 196]
        sectors['Quilicura'] = [557, 831]

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input()
            },
            'selectors': render_to_string('travel/map_selectors.html'),
            'sectors': json.dumps(sectors)
        }

        return render(request, 'travel/map.html', context)


class TripStrategiesHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.travel'

    def get(self, request):
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input(),
                'minutes': get_halfhour_list_for_select_input()
            }
        }
        return render(request, "travel/strategies.html", context)
