# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserActions(models.Model):
    """ save urls called by users """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=300, null=False)
    method = models.CharField(max_length=4, null=False)
    timestamp = models.DateTimeField(default=timezone.now, null=False)
    duration = models.DurationField(null=False)


class UserSession(models.Model):
    """ user session """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField("Inicio", null=False)
    end_time = models.DateTimeField("Final", null=False)
    duration = models.DurationField("Duración", null=False)

    class Meta:
        verbose_name = "sesión de usuario"
        verbose_name_plural = "sesioness de usuarios"


class UserSessionStats(models.Model):
    """ session stats """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_number = models.IntegerField("Número de sesión", null=False)
    last_session_timestamp = models.DateTimeField("Ultima sesión", null=False)
    max_session_duration = models.DurationField("Duración máxima de sesión", null=False)
    min_session_duration = models.DurationField("Duración mínima de sesión", null=False)
    avg_session_duration = models.DurationField("Duración promedio de sesión", null=False)
    total_session_duration = models.DurationField("Duración total de sesión", null=False, default=timedelta())

    class Meta:
        verbose_name = "estadísticas de usuario"
        verbose_name_plural = "estadísticas de usuarios"
