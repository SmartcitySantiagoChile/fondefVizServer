# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def inline_input(label, input_id):
    content = u"""
        <div class="form-group">
            <label for="{1}">{0}:</label>
            <input type="text" class="form-control" id="{1}" />
        </div>
        """

    return format_html(content, label, input_id)