from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def table(id, columns):
    ths = ""
    for _ in range(columns):
        ths += "<th></th>"

    table = """
        <table id="{}" class="table table-striped table-bordered dt-responsive table-condensed nowrap" width="100%">
            <thead>
              <tr>""" + ths + """</tr>
            </thead>
        </table>
        """
    return format_html(table, id)