# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_day_type_list_for_select_input


class IndexHTML(View):
    permission_required = 'localinfo.validation'

    def get(self, request):
        template = "paymentfactor/index.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input()
            }
        }

        return render(request, template, context)
