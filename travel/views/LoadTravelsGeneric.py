#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from django.views.generic import View
from django.core.serializers import serialize
from localinfo.models import TimePeriod, Commune, HalfHour


class LoadTravelsGeneric(View):
    """ generic view to load profile data """

    # elastic search index name
    INDEX_NAME = "travel"

    def __init__(self, additional_es_query_dict):
        self.context = dict()
        self.context.update(self.get_local_info_dict())
        super(LoadTravelsGeneric, self).__init__()

    def get_local_info_dict(self):
        communes = Commune.objects.all()
        halfhours = HalfHour.objects.all()
        timeperiods = TimePeriod.objects.all()

        day_types = list()
        day_types.append({'pk': 0, 'name': 'Laboral'})
        day_types.append({'pk': 1, 'name': 'Sábado'})
        day_types.append({'pk': 2, 'name': 'Domingo'})

        data = dict()
        data['daytypes'] = json.dumps(day_types)
        data['communes'] = serialize('json', communes)
        data['halfhours'] = serialize('json', halfhours)
        data['timeperiods'] = serialize('json', timeperiods)
        return data
