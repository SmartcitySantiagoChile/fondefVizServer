# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def update_button(html_id, label):

    content = """
        <div class="ln_solid"></div>
        <button id="{0}" class="btn btn-success btn-round">{1}</button>
        """

    return format_html(content, html_id, label)
