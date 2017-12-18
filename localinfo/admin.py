# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from localinfo.models import Operator, HalfHour


class OperatorAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('esId', 'name', 'description')


class HalfHourAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('authorityPeriodName', 'name', 'shortName', 'longName')

    def has_add_permission(self, request):
        return False

admin.site.register(Operator, OperatorAdmin)
admin.site.register(HalfHour, HalfHourAdmin)