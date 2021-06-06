from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


@register.simple_tag
def tile_stats(md, sm, xs, items):
    """ create tile for each item in items

    item structure
    {
        "title": "",
        "title_icon": "",
        "value": "",
        "value_id": "",
        "sub_value_id": "",
        "sub_title": ""
    }
    """

    tile_items = []
    for item in items:
        tile = format_html("""
            <div class="col-md-{0} col-sm-{1} col-xs-{2} tile_stats_count">
              <span class="count_top"><i class="fa {3}"></i> {4}</span>
              <div id="{5}" class="count">{6}</div>
              <span class="count_bottom"><i class="green" id="{7}"></i> {8}</span>
            </div>
        """, md, sm, xs, item["title_icon"], item["title"], item["value_id"], item["value"], item["sub_value_id"],
                           item["sub_title"])
        tile_items.append(tile)

    content = """
    <div class="row tile_count">
        {0}
    </div>
    """

    return format_html(content, mark_safe("".join(tile_items)))
