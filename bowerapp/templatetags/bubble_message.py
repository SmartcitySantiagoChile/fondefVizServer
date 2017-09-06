# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def bubble_message(title, content, status):
    html_content = u"""
          <div class="alert alert-{} fade in" role="alert">
            <strong>{}</strong>
            {}
          </div>
          """
    return format_html(html_content, status, content, title)