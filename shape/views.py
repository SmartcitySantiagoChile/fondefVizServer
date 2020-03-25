# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View


class MapHTML(View):
    """ load html map to show route polyline """

    def get(self, request):
        template = "shape/map.html"
        context = {}

        return render(request, template, context)
