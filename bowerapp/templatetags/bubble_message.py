# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def bubble_message(title, content, status):
    html_content = """
        <small>
          <div class="alert alert-{0} fade in" role="alert">
            <strong>{2}</strong>
            {1}
          </div></small>
          """
    return format_html(html_content, status, content, title)
