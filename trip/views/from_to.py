# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.mixins import PermissionRequiredMixin

from localinfo.helper import get_timeperiod_list_for_select_input, get_day_type_list_for_select_input, \
    get_halfhour_list_for_select_input


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
