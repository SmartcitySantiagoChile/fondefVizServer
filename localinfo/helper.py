# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group

from localinfo.models import Operator, Commune, DayType, HalfHour, TimePeriod, TransportMode, GlobalPermission


def _list_parser(list):
    return [{'value': x[0], 'item': x[1]} for x in list]


def _dict_parser(list):
    return {x[0]: x[1] for x in list}


def get_day_type_list_for_select_input(to_dict=False):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser
    return parser(DayType.objects.values_list('esId', 'name'))


def get_operator_list_for_select_input(filter=None, to_dict=False):
    """
    :param filter: list of elasticsearch_id to be returned
    :return: list of dict {esId: elasticsearch_id, text: operator_name}
    """
    parser = _list_parser
    queryset = Operator.objects.values_list('esId', 'name')
    if filter:
        queryset = queryset.filter(esId__in=filter)
    if to_dict:
        parser = _dict_parser
    return parser(queryset)


def get_timeperiod_list_for_select_input(to_dict=False):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser
    return parser(TimePeriod.objects.values_list('esId', 'authorityPeriodName'))


def get_halfhour_list_for_select_input(to_dict=False, format='longName'):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser
    return parser(HalfHour.objects.values_list('esId', format))


def get_commune_list_for_select_input(to_dict=False):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser
    return parser(Commune.objects.values_list('esId', 'name'))


def get_transport_mode_list_for_select_input(to_dict=False):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser
    return parser(TransportMode.objects.values_list('esId', 'name'))


class PermissionBuilder(object):

    def __init__(self):
        pass

    def create_permission_based_on_operators(self):
        """
        Create permissions and groups. It is used when localinfo initialize (see localinfo/apps.py)
        """
        group_names = []
        for operator in Operator.objects.all():
            permission, _ = GlobalPermission.objects.get_or_create(codename=operator.esId,
                                                                   defaults={'name': operator.name.lower()})
            group_names.append((operator.name.capitalize(), permission))

        global_group, _ = Group.objects.get_or_create(name=settings.GLOBAL_PERMISSION_GROUP_NAME)

        for group_name, permission in group_names:
            name = 'Datos de {0}'.format(group_name)
            group, _ = Group.objects.get_or_create(name=name)
            group.permissions.add(permission)
            global_group.permissions.add(permission)

        # create permission to see trip section and historical section
        trip_permission, _ = GlobalPermission.objects.get_or_create(codename='travel', defaults={'name': 'viajes'})
        general_permission, _ = GlobalPermission.objects.get_or_create(
            codename='globalstat', defaults={'name': 'estadísticas generales'})
        advance_group, _ = Group.objects.get_or_create(name='Sección viajes y estadísticas generales')
        advance_group.permissions.add(trip_permission, general_permission)

        # create permissino to see storage section
        storage_permission, _ = GlobalPermission.objects.get_or_create(
            codename='storage', defaults={'name': 'almacenamiento'})
        storage_group, _ = Group.objects.get_or_create(name='Sección de almacenamiento')
        storage_group.permissions.add(storage_permission)

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
