# -*- coding: utf-8 -*-


from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.postgres.search import SearchVector
from django.db import transaction, IntegrityError
from django.utils.translation import gettext_lazy as _

from localinfo.forms import DayDescriptionForm, FAQForm
from localinfo.helper import PermissionBuilder
from localinfo.models import Operator, HalfHour, DayDescription, CalendarInfo, FAQ, OPDictionary

admin.site.unregister(Group)
admin.site.unregister(User)


class OperatorAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('esId', 'name')

    def save_model(self, request, obj, form, change):
        permission_builder = PermissionBuilder()
        if not change:
            super(OperatorAdmin, self).save_model(request, obj, form, change)
            # add permission to global group and create group related with operator after saved
            permission_builder.add_permission(obj)
        elif 'esId' in form.changed_data or 'name' in form.changed_data:
            permission_builder.update_permission(obj)
            super(OperatorAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # delete permission for global group and delete group related with operator after saved
        permission_builder = PermissionBuilder()
        try:
            with transaction.atomic():
                permission_builder.delete_permission(obj)
                super(OperatorAdmin, self).delete_model(request, obj)
        except IntegrityError:
            message = _('El operador no puede ser eliminado porque existen usuarios asignados a ese permiso')
            messages.add_message(request, messages.INFO, message)


class HalfHourAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('authorityPeriodName', 'name', 'shortName', 'longName')
    list_display_links = None

    def has_add_permission(self, request):
        return False


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = []
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login')

    def render_delete_form(self, request, context):
        del context['model_count']
        del context['deleted_objects']

        return super(CustomUserAdmin, self).render_delete_form(request, context)


class DayDescriptionAdmin(admin.ModelAdmin):
    actions = None
    form = DayDescriptionForm
    list_display = ('color', 'description')


class CalendarInfoAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('date', 'day_description')


class FAQSAdmin(admin.ModelAdmin):
    actions = None
    form = FAQForm
    list_display = ('question', 'short_answer', 'category')
    search_fields = ['question', 'answer']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(FAQSAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.annotate(search=SearchVector('question', 'answer', config='french_unaccent')). \
            filter(search=search_term)
        return queryset, use_distinct


class CustomOPDictionaryAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('auth_route_code', 'user_route_code', 'op_route_code', 'route_type', 'created_at', 'updated_at')


admin.site.register(Operator, OperatorAdmin)
admin.site.register(HalfHour, HalfHourAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(DayDescription, DayDescriptionAdmin)
admin.site.register(CalendarInfo, CalendarInfoAdmin)
admin.site.register(FAQ, FAQSAdmin)
admin.site.register(OPDictionary, CustomOPDictionaryAdmin)
