# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.views.generic import View


class LoadBipByOperatorHTML(View):

    def get(self, request):
        template = "bip/byOperator.html"

        context = {
            'tabs': {
                'header': ['Gráfico', 'Mapa'],
                'content': ['<div id="barChart" style="height:600px;"></div>',
                            '<div id="mapid" style="height: 500px;min-height: 500px"></div>']
            }
        }

        return render(request, template, context)
