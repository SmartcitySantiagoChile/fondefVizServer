from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def read_only_field(label, value, unit):
    field = """
        <div class="form-horizontal form-label-left">
          <div class="form-group">
            <label class="control-label col-md-6 col-sm-6 col-xs-12">{}</label>
            <div class="input-group">
              <input class="form-control" readonly="readonly" value="{}" />
              <span class="input-group-addon">{}</span>
            </div>
          </div>
        </div>
        """
    if value is None:
        value = ""

    return format_html(field, label, value, unit)
