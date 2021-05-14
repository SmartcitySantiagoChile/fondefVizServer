# -*- coding: utf-8 -*-

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


@register.simple_tag
def table(html_id, columns, with_checker=True, data=None):
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
    rows = []
    if data is not None:
        for row in data:
            html_row = '<tr>'
            for column in row:
                html_row += '<td>{0}</td>'.format(column)
            rows.append('{0}</tr>'.format(html_row))

    html_table = """
        <div class="table-responsive">
            <table id="{0}" class="table table-striped table-bordered dt-responsive table-condensed nowrap" width="100%">
                <thead>
                  <tr>{1}{2}</tr>
                </thead>
                <tbody>
                    {3}
                </tbody>
            </table>
        </div>
        """

    return format_html(html_table, html_id, mark_safe(checker), mark_safe(ths), mark_safe(''.join(rows)))
