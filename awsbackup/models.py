# -*- coding: utf-8 -*-


from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class DownloadLink(models.Model):
    """ save download link, if it is available """
    filename = models.CharField(max_length=30, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=False)
    expire_at = models.DateTimeField(null=False)
    url = models.URLField(null=False)
    user = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.SET_NULL, null=True)
