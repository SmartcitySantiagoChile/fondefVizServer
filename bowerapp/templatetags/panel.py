# -*- coding: utf-8 -*-


from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def panel(title_icon, title, body, info_target_id='', title_id='', show_collapse=False):
    help_button = '<li><a data-toggle="modal" data-target="#{0}"><i class="fa fa-info-circle"></i></a></li>'. \
        format(info_target_id)
    collapse = '<li><a class="collapse-link"><i class="fa fa-chevron-up"></i></a></li>'
    if not show_collapse:
        collapse = ''
    if not info_target_id:
        help_button = ''

    html_title = '<span id="{1}">{2}</span>'
    if not title_id:
        html_title = '{2}'

    html_header = """
        <div class="x_title">
          <h2><i class="fa {0}"></i> """ + html_title + """</h2>
          <ul class="nav navbar-right panel_toolbox">
          """ + collapse + help_button + """
          </ul>
          <div class="clearfix"></div>
        </div>
        """

    html_content = '<div class="x_content">{3}</div>'
    html_header = html_header if title != "" else ""
    html_panel = '<div class="x_panel">' + html_header + html_content + '</div>'

    return format_html(html_panel, title_icon, title_id, title, body)
