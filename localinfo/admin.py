# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.db import transaction, IntegrityError
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from localinfo.forms import DayDescriptionForm
from localinfo.helper import PermissionBuilder
from localinfo.models import Operator, HalfHour, DayDescription, CalendarInfo, FAQS

admin.site.unregister(Group)
admin.site.unregister(User)


class OperatorAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('esId', 'name')

    def save_model(self, request, obj, form, change):
        permission_builder = PermissionBuilder()
        if not change:
            super(OperatorAdmin, self).save_model(request, obj, form, change)
            # add permission to global group and create group related with operator after saved
            permission_builder.add_permission(obj)
        elif 'esId' in form.changed_data or 'name' in form.changed_data:
            permission_builder.update_permission(obj)
            super(OperatorAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # delete permission for global group and delete group related with operator after saved
        permission_builder = PermissionBuilder()
        try:
            with transaction.atomic():
                permission_builder.delete_permission(obj)
                super(OperatorAdmin, self).delete_model(request, obj)
        except IntegrityError:
            message = _('El operador no puede ser eliminado porque existen usuarios asignados a ese permiso')
            messages.add_message(request, messages.INFO, message)


class HalfHourAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('authorityPeriodName', 'name', 'shortName', 'longName')
    list_display_links = None

    def has_add_permission(self, request):
        return False


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = []


class DayDescriptionAdmin(admin.ModelAdmin):
    actions = None
    form = DayDescriptionForm
    list_display = ('color', 'description')


class CalendarInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('date', 'day_description')


class FAQSAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('title', 'question', 'answer')
    search_fields = ['title', 'question', 'answer']


admin.site.register(Operator, OperatorAdmin)
admin.site.register(HalfHour, HalfHourAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(DayDescription, DayDescriptionAdmin)
admin.site.register(CalendarInfo, CalendarInfoAdmin)
admin.site.register(FAQS, FAQSAdmin)

