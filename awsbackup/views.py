# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from awsbackup.aws import AWSSession
from awsbackup.models import DownloadLink


class TableHTML(PermissionRequiredMixin, View):
    """ html table to see data """
    permission_required = 'localinfo.storage'
    bucket_name = None
    subtitle = None

    def get(self, request):
        template = 'awsbackup/table.html'
        header = ['Nombre', 'Última modificación', 'Tamaño', 'Descargar']
        aws_session = AWSSession()
        table_data = aws_session.retrieve_obj_list(self.bucket_name)

        # TODO: remove this and move to dict
        new_table_data = []
        for row in table_data:
            new_table_data.append([row['name'], row['last_modified'], row['size'], row['url']])

        context = {
            'table_header': header,
            'table_data': new_table_data,
            'subtitle': self.subtitle,
            'bucket_name': self.bucket_name
        }

        return render(request, template, context)


class TableWithoutCalendarHTML(PermissionRequiredMixin, View):
    """ html table to see data """
    permission_required = 'localinfo.storage'
    bucket_name = None
    subtitle = None

    def get(self, request):
        template = 'awsbackup/table_without_calendar.html'
        header = ['Nombre', 'Última modificación', 'Tamaño', 'Descargar']
        aws_session = AWSSession()
        table_data = aws_session.retrieve_obj_list(self.bucket_name)

        # TODO: remove this and move to dict
        new_table_data = []
        for row in table_data:
            new_table_data.append([row['name'], row['last_modified'], row['size'], row['url']])

        context = {
            'table_header': header,
            'table_data': new_table_data,
            'subtitle': self.subtitle,
            'bucket_name': self.bucket_name
        }

        return render(request, template, context)


class AvailableDays(PermissionRequiredMixin, View):
    """ html table to see data """
    permission_required = 'localinfo.storage'

    def get(self, request, bucket_name):
        available_days = AWSSession().get_available_days(bucket_name)

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)


@method_decorator([csrf_exempt], name='dispatch')
class CreateDownloadLink(PermissionRequiredMixin, View):
    """ view to create download link """
    permission_required = 'localinfo.storage'

    def post(self, request):
        bucket_name = request.POST.get('bucket_name')
        filename = request.POST.get('filename')

        now = timezone.now()
        time_windows_in_hours = 24
        time_delta = timezone.timedelta(hours=time_windows_in_hours)

        queryset = DownloadLink.objects.filter(filename=filename, expire_at__gt=now).order_by('-expire_at')
        if not queryset.exists():
            url = AWSSession().create_download_link(filename, bucket_name, time_delta.total_seconds())
            expire_at = now + time_delta
            download_link_obj = DownloadLink.objects.create(filename=filename, created_at=now, expire_at=expire_at,
                                                            url=url)
        else:
            download_link_obj = queryset.first()

        response = {
            'url': download_link_obj.url,
            'expire_at': download_link_obj.expire_at
        }

        return JsonResponse(response)


class ListDownloadLink(PermissionRequiredMixin, View):
    """ view to create download link """
    permission_required = 'localinfo.storage'

    def get(self, request):
        response = {}
        for download_link_obj in DownloadLink.objects.all():
            response[download_link_obj.filename] = {
                'url': download_link_obj.url,
                'expire_at': download_link_obj.expire_at
            }

        return JsonResponse(response)
