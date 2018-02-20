# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from localinfo.models import Operator, Commune, DayType, HalfHour, TimePeriod


def _list_parser(list):
    return [{'value': x[0], 'item': x[1]} for x in list]


def get_day_type_list_for_select_input():
    return _list_parser(DayType.objects.values_list('esId', 'name'))


def get_operator_list_for_select_input():
    return _list_parser(Operator.objects.values_list('esId', 'name'))


def get_timeperiod_list_for_select_input():
    return _list_parser(TimePeriod.objects.values_list('esId', 'authorityPeriodName'))


def get_halfhour_list_for_select_input():
    return _list_parser(HalfHour.objects.values_list('esId', 'name'))


def get_commune_list_for_select_input():
    return _list_parser(Commune.objects.values_list('esId', 'name'))
