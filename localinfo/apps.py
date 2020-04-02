from django.apps import AppConfig

from io import StringIO


class LocalinfoConfig(AppConfig):
    name = 'localinfo'

    def ready(self):
        # create permissions if not exist
        from django.core.management import call_command
        from localinfo.helper import PermissionBuilder

        out = StringIO()
        call_command('showmigrations', '--list', 'localinfo', stdout=out)

        if '[ ]' in out.getvalue():
            return

        PermissionBuilder().create_permission_based_on_operators()
