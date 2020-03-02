from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')
admin.site.register(User, UserAdmin)
