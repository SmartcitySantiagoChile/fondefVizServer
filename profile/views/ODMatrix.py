# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View

from esapi.helper.odbyroute import ESODByRouteHelper

from localinfo.models import HalfHour


class ODMatrixView(View):

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
