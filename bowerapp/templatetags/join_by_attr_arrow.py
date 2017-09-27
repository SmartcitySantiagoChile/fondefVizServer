from django import template

register = template.Library()


@register.filter
def join_by_attr_arrow(the_list, attr_name, separator=u' <i class="fa fa-arrows-h fa-lg" aria-hidden="true"></i> '):
    return separator.join(str(i[attr_name]) for i in the_list)