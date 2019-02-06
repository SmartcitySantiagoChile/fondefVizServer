# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
