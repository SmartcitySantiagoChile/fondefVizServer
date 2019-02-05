# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserActions(models.Model):
    """ save urls called by users """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=300, null=False)
    GET_METHOD = 'get'
    POST_METHOD = 'post'
    METHOD_CHOICES = (
        (GET_METHOD, 'post'),
        (POST_METHOD, 'get')
    )
    method = models.CharField(max_length=4, null=False, choices=METHOD_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now, null=False)
    duration = models.DateTimeField(null=False)
