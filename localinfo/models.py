# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class TimePeriod(models.Model):
    """ Time period with standar names """
    dayType = models.CharField(max_length=8)
    """ Type of day: Working day, Saturday, Sunday """
    transantiagoPeriod = models.CharField(max_length=30)
    """ Standar name """
    initialTime = models.TimeField(auto_now=False, auto_now_add=False)
    """ Initial time for the period """
    endTime = models.TimeField(auto_now=False, auto_now_add=False)
    """ End time for the period """
