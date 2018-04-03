# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.safestring import mark_safe

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
        (None, {'fields': ('file', 'query', 'scaped_filters', 'fileType')}),
        (None, {'fields': ('enqueueTimestamp', 'jobId', 'status')}),
        (None, {'fields': ('executionStart', 'executionEnd')}),
        (None, {'fields': ('errorMessage',)}),
    )
    list_filter = []
    list_display = ('jobId', 'user', 'get_file_link', 'status', 'enqueueTimestamp', 'executionStart', 'executionEnd')
    actions = None

    def get_file_link(self, obj):
        if bool(obj.file):
            return '<a href="{0}">Descargar</a>'.format(obj.file.url)
        return '<a class="disabled" href="#">No hay archivo</a>'
    get_file_link.allow_tags = True
    get_file_link.short_description = 'Descargar archivo'

    def scaped_filters(self, obj):
        return mark_safe(obj.filters)
    scaped_filters.short_description = 'Filtros'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        return 'jobId', 'type', 'status', 'executionStart', 'executionEnd', 'errorMessage', 'enqueueTimestamp', \
               'file', 'query', 'scaped_filters', 'fileType'


admin.site.register(DataSourcePath, DataSourceAdmin)
admin.site.register(UploaderJobExecution, UploaderJobExecutionAdmin)
admin.site.register(ExporterJobExecution, ExporterJobExecutionAdmin)
admin.site.register(LoadFile)
