# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from esapi.helper.profile import ESProfileHelper

from localinfo.models import HalfHour


class LoadProfileByExpeditionHTML(View):

    def get(self, request):
        template = "profile/byExpedition.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]

        es_helper = ESProfileHelper()
        base_params = es_helper.get_base_params()

        context = {
            'data_filter': es_helper.make_multisearch_query_for_aggs(base_params)
        }
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)


class LoadProfileByStopHTML(View):
    def __init__(self):
        super(LoadProfileByStopHTML, self).__init__()
        self.es_helper = ESProfileHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/byStop.html"

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]
        context = {
            'data_filter': self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        }
        context['data_filter']['minutes'] = minutes

        return render(request, template, context)


class ODMatrixHTML(View):

    def get(self, request):
        template = "profile/odmatrix.html"

        es_helper = ESODByRouteHelper()
        # TODO: revisar porque parece que no es necesario esto
        base_params = es_helper.get_base_params()

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)

        context = es_helper.make_multisearch_query_for_aggs(base_params)
        context['minutes'] = minutes

        return render(request, template, context)


class TrajectoryHTML(View):

    def get(self, request):
        template = "profile/trajectory.html"

        es_helper = ESProfileHelper()
        base_params = es_helper.make_multisearch_query_for_aggs(es_helper.get_base_params())

        # add periods of thirty minutes
        minutes = [{'item': m[0], 'value': m[1]} for m in
                   HalfHour.objects.all().order_by("id").values_list("longName", 'esId')]
        context = base_params
        context['minutes'] = minutes

        return render(request, template, context)
