# -*- coding: utf-8 -*-


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
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)
    duration = models.DurationField(null=False)


class UserSessionStats(models.Model):
    """ session stats """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_number = models.IntegerField(null=False)
    last_session_timestamp = models.DateTimeField(null=False)
    max_session_duration = models.DurationField(null=False)
    min_session_duration = models.DurationField(null=False)
    avg_session_duration = models.DurationField(null=False)
