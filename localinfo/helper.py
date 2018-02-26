# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from localinfo.models import Operator, Commune, DayType, HalfHour, TimePeriod


def _list_parser(list):
    return [{'value': x[0], 'item': x[1]} for x in list]


def get_day_type_list_for_select_input():
    return _list_parser(DayType.objects.values_list('esId', 'name'))


def get_operator_list_for_select_input(filter=None):
    """
    :param filter: list of elasticsearch_id to be returned
    :return: list of dict {esId: elasticsearch_id, text: operator_name}
    """
    queryset = Operator.objects.values_list('esId', 'name')
    if not filter:
        queryset = queryset.filter(esId__in=filter)
    return _list_parser(queryset)


def get_timeperiod_list_for_select_input():
    return _list_parser(TimePeriod.objects.values_list('esId', 'authorityPeriodName'))


def get_halfhour_list_for_select_input():
    return _list_parser(HalfHour.objects.values_list('esId', 'name'))


def get_commune_list_for_select_input():
    return _list_parser(Commune.objects.values_list('esId', 'name'))


from django.contrib.auth.models import Group
from django.conf import settings

from localinfo.models import GlobalPermission
from localinfo.models import Operator


class PermissionBuilder(object):

    def __init__(self):
        pass

    def create_permission_based_on_operators(self):
        """
        Create permissions and groups. It is used when localinfo initialize (see localinfo/apps.py)
        """
        group_names = []
        for operator in Operator.objects.all():
            permission, _ = GlobalPermission.objects.get_or_create(codename=operator.esId, name=operator.name.lower())
            group_names.append((operator.name.capitalize(), permission))

        global_group, _ = Group.objects.get_or_create(name=settings.GLOBAL_PERMISSION_GROUP_NAME)

        for group_name, permission in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.add(permission)
            global_group.permissions.add(permission)

    def update_permission(self, new_operator_obj):
        """
        Modify permission if user change name or esId
        """
        old_operator = Operator.objects.get(id=new_operator_obj.id)
        permission = GlobalPermission.objects.get(codename=old_operator.esId)
        permission.codename = new_operator_obj.esId
        permission.name = new_operator_obj.name.lower()
        permission.save()

        group = Group.objects.get(name=old_operator.name.capitalize())
        group.name = new_operator_obj.name.capitalize()
        group.save()

    def add_permission(self, operator_obj):
        """
        create a new permission. It is used when user add new operator
        """
        permission, _ = GlobalPermission.objects.get_or_create(codename=operator_obj.esId,
                                                               name=operator_obj.name.lower())

        group, _ = Group.objects.get_or_create(name=operator_obj.name.capitalize())
        group.permissions.add(permission)

        global_group, _ = Group.objects.get_or_create(name=settings.GLOBAL_PERMISSION_GROUP_NAME)
        global_group.permissions.add(permission)

    def delete_permission(self, operator_obj):
        """
        delete permission related to operator obj
        """
        permission = GlobalPermission.objects.get(codename=operator_obj.esId)

        group = Group.objects.get(name=operator_obj.name.capitalize())
        group.permissions.remove(permission)
        group.delete()

        global_group = Group.objects.get(name=settings.GLOBAL_PERMISSION_GROUP_NAME)
        global_group.permissions.remove(permission)

        permission.delete()

    def get_valid_operator_id_list(self, user):
        """
        return list of operator esId field valid for user
        """
        answer = []
        for esId in Operator.objects.values_list('esId', flat=True):
            if user.has_perm('localinfo.{0}'.format(esId)):
                answer.append(esId)

        return answer
