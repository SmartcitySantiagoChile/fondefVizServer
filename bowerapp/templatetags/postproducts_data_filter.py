from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bowerapp.templatetags.columns import columns
from bowerapp.templatetags.inline_input import inline_input
from bowerapp.templatetags.inline_select import inline_select
from bowerapp.templatetags.panel import panel
from bowerapp.templatetags.update_button import update_button

register = template.Library()


@register.simple_tag
def postproducts_data_filter(data_filter,
                             show_day_filter=False,
                             show_day_type_filter=False,
                             show_commune_filter=False,
                             info_target_id='',
                             show_export_button_1=True,
                             show_export_button_2=True,
                             export_button_1_label='',
                             export_button_2_label=''):
    data_filter = [] if data_filter == '' else data_filter

    filters = [
        {'show': show_day_filter, 'data_key': '', 'input_type': 'text',
         'label': 'Días:', 'js_id': 'dayFilter',
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_day_type_filter, 'data_key': 'day_types', 'input_type': 'select',
         'label': 'Tipo de día:', 'js_id': 'dayTypeFilter', 'multi_select': True,
         'col-xs': 12, 'col-sm': 3, 'col-md': 3},
        {'show': show_commune_filter, 'data_key': 'communes', 'input_type': 'select',
         'label': 'Comunas:', 'js_id': 'multiCommuneFilter', 'multi_select': True,
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

    html_buttons = ''
    if show_export_button_1:
        export_btn_js_id = 'btnExportData'
        export_btn_label = export_button_1_label
        html_export_button = update_button(export_btn_js_id, export_btn_label, 'warning', 'pull-right')
        html_buttons += html_export_button

    if show_export_button_2:
        export_btn_js_id = 'btnExportData2'
        export_btn_label = export_button_2_label
        html_export_button = update_button(export_btn_js_id, export_btn_label, 'warning', 'pull-right')
        html_buttons += html_export_button

    html_button_column = columns(12, 12, 12, html_buttons)
    panel_body += '<div class = "row">' + \
                  columns(12, 12, 12, '<div class="ln_solid"></div>') + \
                  '</div>' + html_button_column

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
