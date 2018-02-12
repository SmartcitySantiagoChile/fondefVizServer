# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from localinfo.models import TimePeriod

from esapi.views.speed import ESSpeedHelper


class SpeedVariationHTML(View):

    def get(self, request):
        template = "speed/variation.html"

        es_helper = ESSpeedHelper()

        context = {
            'dayTypes': TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True),
            'routes': es_helper.get_route_list()
        }

        return render(request, template, context)
