# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DatamanagerConfig(AppConfig):
    name = 'datamanager'

    def ready(self):
        # create permissions if not exist
        from django.contrib.auth.models import Group
        from datamanager.models import GlobalPermission
        from localinfo.models import Operator

        global_permission_name = 'Transantiago'

        group_names = []
        for operator in Operator.objects.all():
            permission, _ = GlobalPermission.objects.get_or_create(codename=operator.esId, name=operator.name.lower())
            group_names.append((operator.name.capitalize(), permission))

        global_group, _ = Group.objects.get_or_create(name=global_permission_name)

        for (group_name, permission) in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.add(permission)
            global_group.permissions.add(permission)
