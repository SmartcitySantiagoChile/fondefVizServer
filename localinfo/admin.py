# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.conf import settings

from localinfo.models import Operator, HalfHour, GlobalPermission

admin.site.unregister(Group)
admin.site.unregister(User)


class OperatorAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('esId', 'name', 'description')

    def save_model(self, request, obj, form, change):
        if not change:
            super(OperatorAdmin, self).save_model(request, obj, form, change)
            # add permission to global group and create group related with operator after saved
            obj.refresh_from_db()
            permission, _ = GlobalPermission.objects.get_or_create(codename=obj.esId, name=obj.name.lower())

            group, _ = Group.objects.get_or_create(name=obj.name.capitalize())
            group.permissions.add(permission)

            global_group, _ = Group.objects.get_or_create(name=settings.GLOBAL_PERMISSION_GROUP_NAME)
            global_group.permissions.add(permission)
        elif 'esId' in form.changed_data or 'name' in form.changed_data:
            old_operator = Operator.objects.get(id=obj.id)
            permission = GlobalPermission.objects.get(codename=old_operator.esId)
            permission.codename = obj.esId
            permission.name = obj.name.lower()
            permission.save()

            group = Group.objects.get(name=old_operator.name.capitalize())
            group.name = obj.name.capitalize()
            group.save()
            super(OperatorAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # delete permission for global group and delete group related with operator after saved
        from django.db import transaction, IntegrityError
        from django.contrib import messages
        try:
            with transaction.atomic():
                permission = GlobalPermission.objects.get(codename=obj.esId)

                group = Group.objects.get(name=obj.name.capitalize())
                group.permissions.remove(permission)
                group.delete()

                global_group = Group.objects.get(name=settings.GLOBAL_PERMISSION_GROUP_NAME)
                global_group.permissions.remove(permission)

                permission.delete()
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


admin.site.register(Operator, OperatorAdmin)
admin.site.register(HalfHour, HalfHourAdmin)
admin.site.register(User, CustomUserAdmin)
