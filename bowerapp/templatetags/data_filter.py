# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bowerapp.templatetags.inline_select import inline_select
from bowerapp.templatetags.inline_input import inline_input
from bowerapp.templatetags.columns import columns
from bowerapp.templatetags.panel import panel
from bowerapp.templatetags.update_button import update_button

register = template.Library()


@register.simple_tag
def data_filter(data_filter,
                show_day_filter=False,
                show_stop_filter=False,
                show_day_type_filter=False,
                show_pass_period_filter=False,
                show_dispatch_period_filter=False,
                show_pass_minute_filter=False,
                show_dispatch_minute_filter=False,
                show_operator_filter=False,
                show_user_route_filter=False,
                show_auth_route_filter=False):

    data_filter = [] if data_filter == '' else data_filter

    filters = [
        {'show': show_day_filter, 'data_key': '', 'input_type': 'text',
         'label': 'Día:', 'js_id': 'dayFilter',
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_stop_filter, 'data_key': 'stops', 'input_type': 'select',
         'label': 'Parada:', 'js_id': 'stopFilter', 'multi_select': False,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_day_type_filter, 'data_key': 'dayTypes', 'input_type': 'select',
         'label': 'Tipo de día:', 'js_id': 'dayTypeFilter', 'multi_select': True,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_pass_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de pasada:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_pass_minute_filter, 'data_key': 'minutes', 'input_type': 'select',
         'label': 'Media hora de pasada:', 'js_id': 'minutePeriodFilter', 'multi_select': True,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_dispatch_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de despacho:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_dispatch_minute_filter, 'data_key': 'minutes', 'input_type': 'select',
         'label': 'Media hora de despacho:', 'js_id': 'minutePeriodFilter', 'multi_select': True,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_operator_filter, 'data_key': 'operators', 'input_type': 'select',
         'label': 'Operador:', 'js_id': 'operatorFilter', 'multi_select': False,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_user_route_filter, 'data_key': 'user_routes', 'input_type': 'select',
         'label': 'Servicio usuario:', 'js_id': 'userRouteFilter', 'multi_select': False,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12},
        {'show': show_auth_route_filter, 'data_key': 'auth_routes', 'input_type': 'select',
         'label': 'Servicio TS:', 'js_id': 'authRouteFilter', 'multi_select': False,
         'col-xs': 3, 'col-sm': 3, 'col-lg': 12}
    ]

    panel_body = ''
    for select_filter in filters:
        if select_filter['show']:
            data = []
            if select_filter['data_key'] in data_filter:
                data = data_filter[select_filter['data_key']]
            html_input = ''
            if select_filter['input_type'] == 'select':
                html_input = inline_select(select_filter['label'], select_filter['js_id'],
                                           data, select_filter['multi_select'])
            elif select_filter['input_type'] == 'text':
                html_input = inline_input(select_filter['label'], select_filter['js_id'])

            html_column = columns(select_filter['col-xs'], select_filter['col-xs'], select_filter['col-xs'],
                                  html_input)
            panel_body += html_column

    # add update button
    btn_js_id = 'btnUpdateData'
    btn_label = 'Actualizar datos'
    html_update_button = update_button(btn_js_id, btn_label)
    html_column = columns(12, 12, 12, html_update_button)
    panel_body += html_column

    panel_icon = 'fa-filter'
    panel_title = 'Filtro'
    html_panel = panel(panel_icon, panel_title, mark_safe(panel_body))

    content = """
<div class="row">
    <div class="col-md-12 col-sm-12 col-xs-12">
        {0}
    </div>
</div>
"""

    return format_html(content, mark_safe(html_panel))
