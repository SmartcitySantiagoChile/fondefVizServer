from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from consistencychecker.models import Consistency


class LoadConsistencyHTML(View):
    """ load  web page to check consistency """

    def get(self, request):
        template = 'consistencychecker/consistency.html'

        return render(request, template, {})


class GetConsistencyData(View):
    """ """

    def get(self, request):
        """ consistency data """

        response = {
            'response': serialize('json', Consistency.objects.all())
        }

        return JsonResponse(response)
