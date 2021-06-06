from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def update_button(html_id, label, type, extra_class=""):
    content = """
        <button id="{0}" class="btn btn-{2} btn-round {3}">{1}</button>
        """

    return format_html(content, html_id, label, type, extra_class)
