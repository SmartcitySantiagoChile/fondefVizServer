# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from awsbackup.aws import AWSSession


class TableHTML(View):
    """ html table to see data """
    bucket_name = None
    subtitle = None

    def get(self, request):
        template = 'awsbackup/table_html.html'

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


class AvailableDays(View):
    """ html table to see data """

    def get(self, request, bucket_name):
        available_days = AWSSession().get_available_days(bucket_name)

        response = {
            'availableDays': available_days
        }

        return JsonResponse(response)
