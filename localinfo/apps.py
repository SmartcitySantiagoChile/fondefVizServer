# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class LocalinfoConfig(AppConfig):
    name = 'localinfo'

    def ready(self):
        # create permissions if not exist
        from django.contrib.auth.models import Group
        from django.conf import settings

        from localinfo.models import GlobalPermission
        from localinfo.models import Operator

        group_names = []
        for operator in Operator.objects.all():
            permission, _ = GlobalPermission.objects.get_or_create(codename=operator.esId, name=operator.name.lower())
            group_names.append((operator.name.capitalize(), permission))

        global_group, _ = Group.objects.get_or_create(name=settings.GLOBAL_PERMISSION_GROUP_NAME)

        for (group_name, permission) in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.add(permission)
            global_group.permissions.add(permission)
