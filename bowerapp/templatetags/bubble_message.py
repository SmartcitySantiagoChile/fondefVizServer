from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def bubble_message(title, content, status):
    html_content = """
        
          <div class="alert alert-{0}" role="alert">
            <strong>{2}</strong>
            {1}
          </div>
          """
    return format_html(html_content, status, content, title)
