# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-21 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0027_auto_20200121_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarinfo',
            name='day_description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='localinfo.DayDescription', verbose_name='Descripci\xf3n de d\xeda'),
        ),
    ]
