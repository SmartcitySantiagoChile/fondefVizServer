# -*- coding: utf-8 -*-

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def toolbar(html_id, *args):
    """
    :param html_id: group id
    :param args: pairs (value, label)
    :return:
    """

    buttons = []
    for index in range(0, len(args), step=2):
        value = args[index]
        label = args[index + 1]
        buttons.append("""
            <label class="btn btn-default"><input type="radio" name="groups" value="{}" checked="">{}</label>
        """.format(value, label))

    content = """
        <div id="{0}" class="btn-toolbar" role="toolbar" data-toggle="buttons">
            <div class="btn-group">
                {1}
            </div>
        </div>
        """

    return format_html(content, html_id, "".join(buttons))
