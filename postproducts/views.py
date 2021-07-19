from django.shortcuts import render
from django.views.generic import View

from localinfo.helper import get_day_type_list_for_select_input, get_commune_list_for_select_input


class TransfersHTML(View):

    def get(self, request):
        template = "postproducts/transfers.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)


class TripsBetweenZonesHTML(View):

    def get(self, request):
        template = "postproducts/tripsBetweenZones.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)


class BoardingAndAlightingByZoneHTML(View):

    def get(self, request):
        template = "postproducts/boardingAndAlightingByZone.html"

        context = {
            'data_filter': {
                'day_types': get_day_type_list_for_select_input(),
                'communes': get_commune_list_for_select_input(),
            },
        }

        return render(request, template, context)
