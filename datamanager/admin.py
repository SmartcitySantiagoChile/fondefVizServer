# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext, gettext_lazy as _

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.unregister(Group)
admin.site.unregister(User)


class MyUserAdmin(UserAdmin):
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = []

admin.site.register(User, MyUserAdmin)
