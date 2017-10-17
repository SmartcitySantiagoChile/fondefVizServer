# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def label(content, status):
    html_content = """
          <span class="label label-{0}">
            {1}
          </span>
          """
    return format_html(html_content, status, content)
