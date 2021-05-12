from django.contrib import admin
from django.utils import timezone
from django.utils.html import mark_safe

from awsbackup.models import DownloadLink


class DownloadLinkAdmin(admin.ModelAdmin):
    """ manager for s3 links """
    fieldsets = (
        (None, {'fields': ('filename', 'url')}),
        (None, {'fields': ('created_at', 'expire_at')}),
    )
    list_filter = []
    list_display = ('filename', 'user', 'created_at', 'expire_at', 'is_active', 'link')
    actions = None

    def is_active(self, obj):
        return obj.expire_at > timezone.now()

    is_active.boolean = True

    def link(self, obj):
        if obj.url is not None:
            return mark_safe(
                "<a href='{0}' class='btn btn-success btn-xs'><i class='fa fa-file'></i> Descargar</a>".format(
                    obj.url))
        else:
            return 'link was not created'

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return 'filename', 'url', 'crated_at', 'expire_at'


admin.site.register(DownloadLink, DownloadLinkAdmin)
