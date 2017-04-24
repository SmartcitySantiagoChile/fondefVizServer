from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection

# Create your views here.

class LoadProfileByExpeditionView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}

    def get(self, request):
        template = "profile/expedition.html"

        return render(request, template, self.context)


class GetLoadProfileByExpeditionData(View):
    ''' '''

    def __init__(self):
        ''' constructor '''
        self.context={}

    def get(self, request):
        ''' expedition data '''
        response = {}
        # use elasticSearch
        

        return JsonResponse(response, safe=False)
