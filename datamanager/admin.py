# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import DataSourcePath
from .models import DataSourceFile


class DataSourceAdmin(admin.ModelAdmin):
    """ manager for data sources """
    fieldsets = (
        (None, {'fields': ('path', 'filePattern')}),
        (None, {'fields': ('code', 'timeStamp')}),
    )
    list_filter = []
    list_display = ('path', 'filePattern', 'code', 'timeStamp')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return ('timeStamp', 'code')


admin.site.register(DataSourcePath, DataSourceAdmin)
