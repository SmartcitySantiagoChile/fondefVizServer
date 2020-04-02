# -*- coding: utf-8 -*-

from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag
def tabs(header_list, content_list):

    tab_children = ''
    for index, header in enumerate(header_list):
        tab_class = ''
        if index == 0:
            tab_class = "active"

        tab_children += """
            <li role = 'presentation' class='{0}'>
              <a href='#tab_content-{1}' id='tab-{1}' role='tab' data-toggle='tab' aria-expanded='true'>{2}</a>
            </li>
            """.format(tab_class, str(index), header)

    tab_content_children = ''
    for index, content in enumerate(content_list):
        tab_class = ''
        if index == 0:
            tab_class = 'fade in active'
        tab_content_children += """
            <div role = 'tabpanel' class='tab-pane {2}' id='tab_content-{0}' aria-labelledby='tab-{0}'>{1}</div>
            """.format(str(index), content, tab_class)

    content = """<div class ='' role='tabpanel' data-example-id='togglable-tabs'>
            <ul id='tabs' class ='nav nav-tabs bar_tabs' role='tablist'>{0}</ul>
            <div id='myTabContent' class='tab-content'>{1}</div></div>
        """.format(tab_children, tab_content_children)

    return mark_safe(content)
