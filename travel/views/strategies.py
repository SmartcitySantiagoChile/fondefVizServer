# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin

from localinfo.helper import get_timeperiod_list_for_select_input, get_day_type_list_for_select_input, \
    get_halfhour_list_for_select_input


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
