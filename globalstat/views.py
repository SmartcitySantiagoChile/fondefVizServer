from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import View

from esapi.views.resume import DICTIONARY


class ResumeHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def get(self, request):
        template = 'globalstat/resume.html'

        attributes = []
        for key, value in DICTIONARY.items():
            if key == 'dayType':
                continue
            attributes.append({
                'value': key,
                'item': value['name']
            })

        context = {
            'data_filter': {
                'metrics': attributes
            }
        }

        return render(request, template, context)


class DetailHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.globalstat'

    def get(self, request):
        template = 'globalstat/detail.html'

        context = {}

        attributes = []
        for key, value in DICTIONARY.items():
            if key == 'dayType':
                continue
            attributes.append({
                'value': key,
                'item': value['name']
            })

        context['metrics'] = attributes

        context['tiles_1'] = [
            {'title': DICTIONARY['version']['name'], 'title_icon': 'fa-barcode', 'value': '',
             'value_id': 'version', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['dayType']['name'], 'title_icon': 'fa-calendar', 'value': '',
             'value_id': 'dayType', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['smartcardNumber']['name'], 'title_icon': 'fa-credit-card', 'value': '',
             'value_id': 'smartcardNumber', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['transactionNumber']['name'], 'title_icon': 'fa-group', 'value': '',
             'value_id': 'transactionNumber', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['expeditionNumber']['name'], 'title_icon': 'fa-group', 'value': '',
             'value_id': 'expeditionNumber', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['GPSPointsNumber']['name'], 'title_icon': 'fa-truck', 'value': '',
             'value_id': 'GPSPointsNumber', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['licensePlateNumber']['name'], 'title_icon': 'fa-truck', 'value': '',
             'value_id': 'licensePlateNumber', 'sub_value_id': '', 'sub_title': ''},
        ]

        context['tiles_2'] = [
            {'title': DICTIONARY['tripNumber']['name'], 'title_icon': 'fa-rocket', 'value': '',
             'value_id': 'tripNumber', 'sub_value_id': '', 'sub_title': ''},
        ]

        context['tiles_22'] = [
            {'title': DICTIONARY['tripsThatUseMetro']['name'], 'title_icon': 'fa-rocket', 'value': '',
             'value_id': 'tripsThatUseMetro', 'sub_value_id': 'validTripNumber', 'sub_title': ''},
            {'title': DICTIONARY['tripsWithOnlyMetro']['name'], 'title_icon': 'fa-train', 'value': '',
             'value_id': 'tripsWithOnlyMetro', 'sub_value_id': '', 'sub_title': ''},
            {'title': DICTIONARY['tripsWithoutLastAlighting']['name'], 'title_icon': 'fa-globe', 'value': '',
             'value_id': 'tripsWithoutLastAlighting', 'sub_value_id': '', 'sub_title': ''},
        ]
        context['tiles_3'] = [
            {'title': DICTIONARY['expeditionNumber']['name'], 'title_icon': 'fa-truck', 'value': '',
             'value_id': 'expeditionNumber', 'sub_value_id': 'date', 'sub_title': ''},
            {'title': DICTIONARY['averageExpeditionTime']['name'], 'title_icon': 'fa-repeat', 'value': '',
             'value_id': 'averageExpeditionTime', 'sub_value_id': '', 'sub_title': 'Minutos'},
            {'title': DICTIONARY['minExpeditionTime']['name'], 'title_icon': 'fa-repeat', 'value': '',
             'value_id': 'minExpeditionTime', 'sub_value_id': '', 'sub_title': 'Minutos'},
            {'title': DICTIONARY['maxExpeditionTime']['name'], 'title_icon': 'fa-repeat', 'value': '',
             'value_id': 'maxExpeditionTime', 'sub_value_id': 'validTripNumber', 'sub_title': 'Minutos'},
            {'title': DICTIONARY['licensePlateNumber']['name'], 'title_icon': 'fa-truck', 'value': '',
             'value_id': 'licensePlateNumber', 'sub_value_id': '', 'sub_title': ''},
        ]

        return render(request, template, context)
