# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string

from localinfo.helper import get_timeperiod_list_for_select_input, get_day_type_list_for_select_input


class MapHTML(View):

    def get(self, request):
        context = {
            'data_filter': {
                'dayTypes': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input()
            },
            'selectors': render_to_string('travel/map_selectors.html')
        }

        return render(request, 'travel/map.html', context)
