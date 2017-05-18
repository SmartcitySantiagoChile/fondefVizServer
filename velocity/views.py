from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection
from django.conf import settings

# from elasticsearch_dsl import Search, Q, A
# # Create your views here.
#
# from localinfo.models import TimePeriod
#
# from errors import ESQueryDoesNotHaveParameters
#
# INDEX_NAME="profiles"
# # elastic search index name

class LoadRankingView(View):
    ''' '''

    def __init__(self):
        ''' contructor '''
        self.context={}
        # self.context['dayTypes'] = TimePeriod.objects.all().distinct('dayType').values_list('dayType', flat=True)
        # self.context['periods'] = TimePeriod.objects.filter(dayType='Laboral').order_by('id').values_list('transantiagoPeriod', flat=True)
        # self.context['routes'] = self.getRouteList()

    def get(self, request):
        template = "velocity/ranking.html"

        return render(request, template, self.context)
