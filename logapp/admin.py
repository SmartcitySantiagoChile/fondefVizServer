# -*- coding: utf-8 -*-


from django.contrib import admin

from logapp.models import UserSession, UserSessionStats


class UserSessionAdmin(admin.ModelAdmin):
    """ manager for user session """
    list_filter = []
    list_display = ('user', 'start_time', 'end_time', 'duration')
    actions = None

    def get_queryset(self, request):
        qs = super(UserSessionAdmin, self).get_queryset(request).order_by('-start_time')
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        return 'user', 'start_time', 'end_time', 'duration'


class UserSessionStatsAdmin(admin.ModelAdmin):
    """ manager for session stats """
    list_filter = []
    list_display = ('user', 'session_number', 'last_session_timestamp', 'max_session_duration', 'min_session_duration',
                    'avg_session_duration', 'total_session_duration')
    actions = None

    def get_queryset(self, request):
        qs = super(UserSessionStatsAdmin, self).get_queryset(request).order_by('-last_session_timestamp')
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        return 'user', 'session_number', 'last_session_timestamp', 'max_session_duration', 'min_session_duration', 'avg_session_duration'


admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(UserSessionStats, UserSessionStatsAdmin)
