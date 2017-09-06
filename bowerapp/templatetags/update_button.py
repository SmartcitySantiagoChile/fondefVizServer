# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def update_button(id, name):

    content = u"""
        <div class="ln_solid"></div>
        <button id="{0}" class="btn btn-success btn-round">{1}</button>
        """

    return format_html(content, id, name)