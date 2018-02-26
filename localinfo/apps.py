# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class LocalinfoConfig(AppConfig):
    name = 'localinfo'

    def ready(self):
        # create permissions if not exist
        from localinfo.helper import PermissionBuilder

        PermissionBuilder().create_permission_based_on_operators()
