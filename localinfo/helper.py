# -*- coding: utf-8 -*-
import csv
from datetime import date as dt

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.postgres.search import SearchVector
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.utils import timezone

from localinfo.models import Operator, Commune, DayType, HalfHour, TimePeriod, TransportMode, GlobalPermission, \
    CalendarInfo, FAQ, OPDictionary, TimePeriodDate


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


def get_timeperiod_list_for_select_input(to_dict=False, filter_id=None):
    parser = _list_parser
    if to_dict:
        parser = _dict_parser

    queryset = TimePeriod.objects.all()
    if filter_id is not None:
        queryset = queryset.filter(date_id=filter_id)

    return parser(queryset.values_list('esId').annotate(
        name=Concat('authorityPeriodName', Value(' ('), 'initialTime', Value('-'), 'endTime', Value(')'),
                    output_field=CharField())))


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


def get_calendar_info():
    """
    :return: all calendar info
    """
    query = CalendarInfo.objects.select_related('day_description')
    result = list()
    for info in query:
        info = {
            "date": info.date,
            "color": info.day_description.color,
            "description": info.day_description.description
        }
        result.append(info)
    return result


def get_all_faqs():
    """
    :return: all faqs
    """
    query = FAQ.objects.all()
    grouped = dict()
    for info in query:
        grouped.setdefault(info.category, []).append(info)
    return grouped


def search_faq(searchText):
    """
    :param search:
    :return: all faqs matched "search"
    """
    query = FAQ.objects.annotate(search=SearchVector('question', 'answer', config='french_unaccent')) \
        .filter(search=searchText)
    grouped = dict()
    for info in query:
        grouped.setdefault(info.category, []).append(info)
    return grouped


def get_op_route(auth_route_code):
    """
    :param auth_route_code:
    :return: op_route_code matched with auth_route_code
    """
    try:
        res = OPDictionary.objects.get(auth_route_code=auth_route_code).op_route_code
    except OPDictionary.DoesNotExist:
        return None
    return res


def get_op_routes_dict():
    """
    :return: dict {auth_route_code: route_type}
    """
    routes_dict = {}
    for auth_route_code, route_type in OPDictionary.objects.values_list('auth_route_code', 'route_type'):
        routes_dict.update({auth_route_code: route_type})
    return routes_dict


def get_valid_time_period_date(date_list):
    """
    :param date_list:
    :return: (valid | not_valid, period_date_id)
    """
    valid_dates = TimePeriodDate.objects.values('date', 'id')
    period_date_valid = ''
    first_date = dt.fromisoformat(date_list[0])
    last_date = dt.fromisoformat(date_list[-1])
    for valid_date in valid_dates:
        if first_date < valid_date['date'] <= last_date:
            return False, ''
        else:
            if first_date >= valid_date['date']:
                period_date_valid = valid_date['id']
    return True, period_date_valid


def upload_csv_op_dictionary(csv_file):
    upload_time = timezone.now()
    reader = csv.reader(csv_file, delimiter=',')
    to_update = []
    to_create = []
    for row in reader:
        if row[1].strip():
            try:
                op_dict_obj = OPDictionary.objects.get(auth_route_code=row[0])
                op_dict_obj.user_route_code = row[1]
                op_dict_obj.op_route_code = row[2]
                op_dict_obj.route_type = row[3]
                op_dict_obj.updated_at = upload_time
                to_update.append(op_dict_obj)

            except OPDictionary.DoesNotExist:
                to_create.append(OPDictionary(user_route_code=row[1], op_route_code=row[2],
                                              route_type=row[3], created_at=upload_time,
                                              updated_at=upload_time,
                                              auth_route_code=row[0]))
    OPDictionary.objects.bulk_create(to_create)
    OPDictionary.objects.bulk_update(to_update,
                                     ['user_route_code', 'op_route_code', 'route_type', 'updated_at'])


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

        # create permission to see storage section
        storage_permission, _ = GlobalPermission.objects.get_or_create(
            codename='storage', defaults={'name': 'almacenamiento'})
        storage_group, _ = Group.objects.get_or_create(name='Sección de almacenamiento')
        storage_group.permissions.add(storage_permission)

        # create permission to see bus station distribution section
        storage_permission, _ = GlobalPermission.objects.get_or_create(
            codename='validation', defaults={'name': 'validaciones'})
        storage_group, _ = Group.objects.get_or_create(name='Sección de validaciones')
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
