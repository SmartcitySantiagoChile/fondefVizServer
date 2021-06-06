from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def header(title, subtitle="", right=""):
    content = """
      <div class="page-title">
        <div class="title_left">
          <h3>{0} <small>{1}</small></h3>
        </div>
        <div class="title_right">
          {2}
        </div>
      </div>
      <div class="clearfix"></div>
    """
    return format_html(content, title, subtitle, right)
