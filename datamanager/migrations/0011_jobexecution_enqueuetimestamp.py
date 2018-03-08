# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-08 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0010_auto_20180308_0608'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobexecution',
            name='enqueueTimestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Encolado'),
            preserve_default=False,
        ),
    ]
