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
                show_get_in_period_filter=False,
                show_pass_period_filter=False,
                show_dispatch_period_filter=False,
                show_pass_minute_filter=False,
                show_dispatch_minute_filter=False,
                show_operator_filter=False,
                show_user_route_filter=False,
                show_auth_route_filter=False,
                show_slider_hour_filter=False,
                show_boarding_period_filter=False,
                show_metric_filter=False,
                show_start_trip_period_filter=False,
                show_start_trip_minute_filter=False,
                show_export_button=True,
                show_exlude_date_filter=False,
                extra_html='',
                info_target_id=''):
    data_filter = [] if data_filter == '' else data_filter

    filters = [
        {'show': show_day_filter, 'data_key': '', 'input_type': 'text',
         'label': 'Días:', 'js_id': 'dayFilter',
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_exlude_date_filter, 'data_key': '', 'input_type': 'text',
         'label': 'Días a excluir:', 'js_id': 'removeDayFilter',
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_stop_filter, 'data_key': 'stops', 'input_type': 'select',
         'label': 'Parada:', 'js_id': 'stopFilter', 'multi_select': False,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_day_type_filter, 'data_key': 'day_types', 'input_type': 'select',
         'label': 'Tipo de día:', 'js_id': 'dayTypeFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_get_in_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de subida en parada:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_pass_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de pasada:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_pass_minute_filter, 'data_key': 'minutes', 'input_type': 'select',
         'label': 'Media hora de pasada:', 'js_id': 'minutePeriodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_dispatch_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de despacho:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_dispatch_minute_filter, 'data_key': 'minutes', 'input_type': 'select',
         'label': 'Media hora de despacho:', 'js_id': 'minutePeriodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_operator_filter, 'data_key': 'operators', 'input_type': 'select',
         'label': 'Operador:', 'js_id': 'operatorFilter', 'multi_select': False,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_user_route_filter, 'data_key': 'user_routes', 'input_type': 'select',
         'label': 'Servicio usuario:', 'js_id': 'userRouteFilter', 'multi_select': False,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_auth_route_filter, 'data_key': 'auth_routes', 'input_type': 'select',
         'label': 'Servicio TS:', 'js_id': 'authRouteFilter', 'multi_select': False,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_slider_hour_filter, 'data_key': '', 'input_type': 'text',
         'label': 'Rango horario:', 'js_id': 'hourRangeFilter',
         'col-xs': 12, 'col-sm': 6, 'col-md': 6},
        {'show': show_boarding_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de subida:', 'js_id': 'boardingPeriodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_metric_filter, 'data_key': 'metrics', 'input_type': 'select',
         'label': 'Métrica(s):', 'js_id': 'metricFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 9, 'col-md': 9},
        {'show': show_start_trip_period_filter, 'data_key': 'periods', 'input_type': 'select',
         'label': 'Período de inicio de viajes:', 'js_id': 'periodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_start_trip_minute_filter, 'data_key': 'minutes', 'input_type': 'select',
         'label': 'Media hora de inicio de viajes:', 'js_id': 'minutePeriodFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3}
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

            html_column = columns(select_filter['col-md'], select_filter['col-sm'], select_filter['col-xs'],
                                  html_input)
            panel_body += html_column

    # add extra html
    panel_body += extra_html

    # add update button
    update_btn_js_id = 'btnUpdateData'
    update_btn_label = 'Actualizar datos'
    html_update_button = update_button(update_btn_js_id, update_btn_label, 'success')

    html_buttons = html_update_button
    if show_export_button:
        export_btn_js_id = 'btnExportData'
        export_btn_label = 'Descargar datos crudos'
        html_export_button = update_button(export_btn_js_id, export_btn_label, 'warning', 'pull-right')
        html_buttons += html_export_button

    html_button_column = columns(12, 12, 12, html_buttons)
    panel_body += '<div class = "row">' + columns(12,12,12, '<div class="ln_solid"></div>') + '</div>' + html_button_column

    panel_icon = 'fa-filter'
    panel_title = 'Filtro'
    html_panel = panel(panel_icon, panel_title, mark_safe(panel_body), info_target_id=info_target_id)

    content = """
        <div class="row">
            <div class="col-md-12 col-sm-12 col-xs-12">
                {0}
            </div>
        </div>
        """

    return format_html(content, mark_safe(html_panel))
