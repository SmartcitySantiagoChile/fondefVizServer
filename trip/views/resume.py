# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.mixins import PermissionRequiredMixin

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input


class ResumeHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.travel'

    def get(self, request):
        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'periods': get_timeperiod_list_for_select_input()
            },
            'indicators': render_to_string('travel/resume_indicators.html'),
            'chart': render_to_string('travel/resume_chart.html'),
        }

        return render(request, 'travel/resume.html', context)
