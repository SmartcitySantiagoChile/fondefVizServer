# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter
def join_by_attr(the_list, attr_name, separator=' , '):
    return separator.join(str(i[attr_name]) for i in the_list)
