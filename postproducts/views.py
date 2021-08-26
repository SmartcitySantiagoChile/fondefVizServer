from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin

from localinfo.helper import get_day_type_list_for_select_input, get_commune_list_for_select_input


class TransfersHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.postproducts'

    def get(self, request):
        template = "postproducts/transfers.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)


class TripsBetweenZonesHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.postproducts'

    def get(self, request):
        template = "postproducts/tripsBetweenZones.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)


class BoardingAndAlightingByZoneHTML(PermissionRequiredMixin, View):
    permission_required = 'localinfo.postproducts'

    def get(self, request):
        template = "postproducts/boardingAndAlightingByZone.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)
