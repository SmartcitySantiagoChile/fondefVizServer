# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string

from travel.views.generic import LoadTravelsGeneric

from localinfo.models import TimePeriod, Commune, HalfHour


class ResumeHTML(View):

    def get(self, request):

        communes = Commune.objects.all()
        halfhours = HalfHour.objects.all()
        timeperiods = TimePeriod.objects.all()

        day_types = list()
        day_types.append({'pk': 0, 'name': 'Laboral'})
        day_types.append({'pk': 1, 'name': 'Sábado'})
        day_types.append({'pk': 2, 'name': 'Domingo'})

        context = {
            'data_filter': {
                'daytypes': json.dumps(day_types),
                'communes': serialize('json', communes),
                'halfhours': serialize('json', halfhours),
                'timeperiods': serialize('json', timeperiods)
            }
        }
        context.update({
            'indicators': render_to_string('travel/resume_indicators.html'),
            'chart': render_to_string('travel/resume_chart.html')
        })
        return render(request, "travel/resume.html", self.context)
