# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from helper import get_calendar_info


class CalendarInfo(View):
    def get(self, request):

        data = get_calendar_info()
        print(data)
        response = {
            'info': data
        }
        return JsonResponse(response)
