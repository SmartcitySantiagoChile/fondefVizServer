# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def tabs(header_list, content_list):

    root_div_init = "<div class ='' role='tabpanel' data-example-id='togglable-tabs' >"
    tab_parent_init = "<ul id='tabs' class ='nav nav-tabs bar_tabs' role='tablist' >"

    tab_children = ""
    for index, header in enumerate(header_list):
        tab_class = ""
        if index == 0:
            tab_class = "active"

        tab_children += \
            "<li role = 'presentation' class='" + tab_class + "'>" +\
              "<a href='#tab_content-" + str(index) + "' id='tab-" + str(index) + "' role='tab' data-toggle='tab' aria-expanded='true'> " + header + " </a>" +\
            "</li>"

    tab_parent_end = "</ul>"
    tab_content_parent_init = "<div id='myTabContent' class='tab-content'>"

    tab_content_children = ""
    for index, content in enumerate(content_list):
        tab_content_children += "< div role = 'tabpanel' class='tab-pane fade active in' id='tab_content-" + str(index) + "' aria-labelledby='tab-" + str(index) + "' >" + \
                                   content + \
                                 "</div>"

    tab_content_parent_end = "</div>"
    root_div_end = "</div>"
    content = root_div_init + tab_parent_init + tab_content_parent_init + tab_content_children + \
              tab_content_parent_end + tab_parent_end + root_div_end
    return format_html(content)