# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def columns(md, sm, xs, body):

    content = u"""
        <div class='col-md-{0} col-sm-{1} col-xs-{2}'>
        {3}
        </div>
        """

    return format_html(content, md, sm, xs, body)