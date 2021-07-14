from django.shortcuts import render

from django.views.generic import View


class TransfersHTML(View):

    def get(self, request):
        template = "postproducts/transfers.html"
        context = {}

        return render(request, template, context)


class TripsBetweenZonesHTML(View):

    def get(self, request):
        template = "postproducts/tripsBetweenZones.html"
        context = {}

        return render(request, template, context)


class BoardingAndAlightingByZoneHTML(View):

    def get(self, request):
        template = "postproducts/boardingAndAlightingByZone.html"
        context = {}

        return render(request, template, context)
