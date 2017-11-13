# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def table(html_id, columns, with_checker=True):
    ths = ""
    if isinstance(columns, list):
        for header in columns:
            ths += "<th>{0}</th>".format(header)
    else:
        for _ in range(columns):
            ths += "<th></th>"

    checker = ""
    if with_checker:
        checker = """
        <th style='padding-right:5px;'>
            <input type='checkbox' id='checkbox-select-all' class='flat' checked>
        </th>
        """

    html_table = """
        <table id="{}" class="table table-striped table-bordered dt-responsive table-condensed nowrap" width="100%">
            <thead>
              <tr>""" + checker + ths + """</tr>
            </thead>
            <tbody>
            </tbody>
        </table>
        """

    return format_html(html_table, html_id)
