# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def tabs(header_list, content_list):

    html_content_part1 = "<div class ='' role='tabpanel' data-example-id='togglable-tabs' >" +\
        "<ul id='tabs' class ='nav nav-tabs bar_tabs' role='tablist' >"

    tabs = ""
    for index, header in enumerate(header_list):
        tab_class = ""
        if index == 0:
            tab_class = "active"

        tabs += "<li role = 'presentation' class='" + tab_class + "'>" +\
            "<a href='#tab_content" + str(index) + "' id='tab-" + str(index) + "' role='tab' data-toggle='tab' aria-expanded='true'> " + header + " </a>" +\
            "</li>"

    html_content_part2 = "</ul><div id='myTabContent' class='tab-content'>"

    tabs_content = ""
    for index, content in enumerate(content_list):
        tabs_content += "< div role = 'tabpanel' class='tab-pane fade active in' id='tab_content" + str(index) + "' aria-labelledby='tab-" + str(index) + "' >" + content + "</div>"

    content = html_content_part1 + tabs + html_content_part2 + tabs_content + "</div>"
    return format_html(content)