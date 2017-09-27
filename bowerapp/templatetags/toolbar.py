# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

import uuid

@register.simple_tag
def toolbar(id, *args):
    """
    :param id: group id
    :param args: pairs (value, label)
    :return:
    """

    buttons = []
    for index in range(0, len(args), step=2):
        value = args[index]
        label = args[index + 1]
        buttons.append(u"""
            <label class="btn btn-default"><input type="radio" name="groups" value="{}" checked="">{}</label>
        """.format(value, label))

    content = u"""
        <div id="{}" class="btn-toolbar" role="toolbar" data-toggle="buttons">
            <div class="btn-group">
                """ + "".join(buttons) + """
            </div>
        </div>
        """

    return format_html(content, id)