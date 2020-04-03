# -*- coding: utf-8 -*-

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def button(html_id, label, style="success", size=""):

    content = """
        <button id="{0}" class="btn btn-{2} btn-round btn-{3}">{1}</button>
        """

    return format_html(content, html_id, label, style, size)
