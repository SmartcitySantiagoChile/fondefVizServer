# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from datamanager.models import DataSourcePath, JobExecution


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
        return 'timeStamp', 'code'


class JobExecutionAdmin(admin.ModelAdmin):
    """ manager for job execution """
    fieldsets = (
        (None, {'fields': ('jobId', 'type', 'status')}),
        (None, {'fields': ('executionStart', 'executionEnd')}),
        (None, {'fields': ('inputs', 'errorMessage')}),
    )
    list_filter = []
    list_display = ('jobId', 'type', 'status', 'executionStart', 'executionEnd')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return 'jobId', 'type', 'status', 'executionStart', 'executionEnd', 'inputs', 'errorMessage'


admin.site.register(DataSourcePath, DataSourceAdmin)
admin.site.register(JobExecution, JobExecutionAdmin)
