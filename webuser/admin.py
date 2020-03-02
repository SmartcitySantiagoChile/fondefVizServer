from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User

admin.site.unregister(User)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')


admin.site.register(User, UserProfileAdmin)
