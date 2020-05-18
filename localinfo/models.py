# -*- coding: utf-8 -*-


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags


class TimePeriod(models.Model):
    """ Time period with standard names """

    # Type of day: Working day, Saturday, Sunday
    dayType = models.CharField(max_length=8)

    # Id which is used on Elastic Search database
    esId = models.IntegerField()

    # Period standard name
    authorityPeriodName = models.CharField(max_length=30)

    # Initial time for the period
    initialTime = models.TimeField(auto_now=False, auto_now_add=False)

    # End time for the period
    endTime = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return str(self.authorityPeriodName)


class Commune(models.Model):
    """ Standard commune data """

    # Id which is used on Elastic Search database
    esId = models.IntegerField()

    # Commune name on adatrap
    name = models.CharField(max_length=50)

    # Commune name, pretty version
    prettyName = models.CharField(max_length=50)

    def __str__(self):
        return str(self.prettyName)


class HalfHour(models.Model):
    """ Represents day time ranges by half hours """

    # Id which is used on Elastic Search database
    esId = models.IntegerField("Identificador")

    # Full half hour representation: HH:MM:00
    name = models.CharField("Nombre", max_length=10)

    # Abbr half hour representation: HH:MM
    shortName = models.CharField("Nombre corto", max_length=10)

    # full description: [HH:MM-HH:MM)
    longName = models.CharField("Nombre largo", max_length=20)

    authorityPeriodName = models.CharField("Período Transantiago", max_length=50)

    def __str__(self):
        return str(self.shortName)

    class Meta:
        verbose_name = "Período de media hora"
        verbose_name_plural = "Períodos de media hora"


class Operator(models.Model):
    """ operator code that exist in elasticsearch """
    esId = models.IntegerField("Identificador", unique=True, null=False)
    name = models.CharField("Nombre", max_length=50, unique=True)

    class Meta:
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"


class DayType(models.Model):
    """ operator code that exist in elasticsearch """
    esId = models.IntegerField("Identificador", unique=True, null=False)
    name = models.CharField("Nombre", max_length=50)
    name = models.CharField("Nombre", max_length=50)

    class Meta:
        verbose_name = "Tipo de día"
        verbose_name_plural = "Tipos de día"


class TransportMode(models.Model):
    """ transport modes used on trips """
    esId = models.IntegerField("Identificador", unique=True, null=False)
    name = models.CharField("Nombre", max_length=50)

    class Meta:
        verbose_name = "Modo de transporte"
        verbose_name_plural = "Modos de transporte"


class GlobalPermissionManager(models.Manager):
    def get_queryset(self):
        return super(GlobalPermissionManager, self). \
            get_queryset().filter(content_type__model='global_permission')


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
        verbose_name = "global_permission"
        default_permissions = ()

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        self.content_type = ct
        super(GlobalPermission, self).save(*args)


class DayDescription(models.Model):
    """color and description for days"""

    color = models.CharField(max_length=7)
    description = models.CharField("Descripción", max_length=250)

    class Meta:
        verbose_name = "descripción de día"
        verbose_name_plural = "descripciónes de días"

    def __str__(self):
        return str(self.description)


class CalendarInfo(models.Model):
    """"Calendar's daydescription information"""

    date = models.DateField("Fecha", unique=True)
    day_description = models.ForeignKey(DayDescription, on_delete=models.CASCADE, verbose_name="Descripción de día")

    class Meta:
        verbose_name = "información de calendario"
        verbose_name_plural = "información de calendario"


class FAQ(models.Model):
    """Frequently asked questions"""

    question = models.TextField("Pregunta")
    answer = models.TextField("Respuesta")

    ROUTE = 'route'
    SPEED = 'speed'
    TRIP = 'trip'
    PROFILE = 'profile'
    PAYMENT_FACTOR = 'paymentfactor'
    ADMIN = 'administration'
    STORAGE = 'storage'
    GLOBAL = 'global'
    GENERAL = 'general'
    FILE_TYPE_CHOICES = (
        (GENERAL, "General"),
        (ADMIN, "Administración"),
        (STORAGE, "Almacenamiento"),
        (PAYMENT_FACTOR, 'Transacciones'),
        (PROFILE, 'Perfil de carga'),
        (SPEED, 'Velocidades'),
        (ROUTE, 'Rutas'),
        (TRIP, 'Viajes'),
        (GLOBAL, 'Estadísticas Globales')
    )
    category = models.CharField('Categoría', max_length=30, null=False, default=GENERAL, choices=FILE_TYPE_CHOICES)

    class Meta:
        verbose_name = "pregunta frecuente"
        verbose_name_plural = "preguntas frecuentes"

    def short_answer(self):
        text_safe = strip_tags(self.answer)
        answer = truncatechars(text_safe, 200)
        return answer

    short_answer.short_description = 'Respuesta'


class CustomRoute(models.Model):
    """"CustomRouteCode-AuthRouteCode dictionary """

    auth_route_code = models.CharField("Código transantiago", max_length=20, unique=True)
    custom_route_code = models.CharField("Código custom", max_length=30)

    class Meta:
        verbose_name = "diccionario de servicios"
        verbose_name_plural = "diccionario de servicios"
