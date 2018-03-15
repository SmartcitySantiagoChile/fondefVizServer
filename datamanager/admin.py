# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from datamanager.models import DataSourcePath, UploaderJobExecution, ExporterJobExecution, LoadFile


class DataSourceAdmin(admin.ModelAdmin):
    """ manager for data sources """
    fieldsets = (
        (None, {'fields': ('path', 'filePattern')}),
        (None, {'fields': ('indexName', 'timeStamp')}),
    )
    list_filter = []
    list_display = ('path', 'filePattern', 'indexName', 'timeStamp')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return 'timeStamp', 'code'


class UploaderJobExecutionAdmin(admin.ModelAdmin):
    """ manager for job execution """
    fieldsets = (
        (None, {'fields': ('file', 'enqueueTimestamp')}),
        (None, {'fields': ('jobId', 'status')}),
        (None, {'fields': ('executionStart', 'executionEnd')}),
        (None, {'fields': ('errorMessage',)}),
    )
    list_filter = []
    list_display = ('jobId', 'file', 'status', 'executionStart', 'executionEnd')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        return 'jobId', 'type', 'status', 'executionStart', 'executionEnd', 'errorMessage', 'enqueueTimestamp', 'file'


class ExporterJobExecutionAdmin(admin.ModelAdmin):
    """ manager for job execution """
    fieldsets = (
        (None, {'fields': ('file', 'query')}),
        (None, {'fields': ('enqueueTimestamp', 'jobId', 'status')}),
        (None, {'fields': ('executionStart', 'executionEnd')}),
        (None, {'fields': ('errorMessage',)}),
    )
    list_filter = []
    list_display = ('jobId', 'file', 'status', 'executionStart', 'executionEnd')
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        return 'jobId', 'type', 'status', 'executionStart', 'executionEnd', 'errorMessage', 'enqueueTimestamp', \
               'file', 'query'


admin.site.register(DataSourcePath, DataSourceAdmin)
admin.site.register(UploaderJobExecution, UploaderJobExecutionAdmin)
admin.site.register(ExporterJobExecution, ExporterJobExecutionAdmin)
admin.site.register(LoadFile)
