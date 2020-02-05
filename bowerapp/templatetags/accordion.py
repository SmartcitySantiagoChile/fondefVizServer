from __future__ import unicode_literals

from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def accordion(content):
    div = '<div class = "accordion" id="accordion" role="tablist" aria-multiselectable="true></div>'
    print(content)
    return format_html("""html_content, status, content""")