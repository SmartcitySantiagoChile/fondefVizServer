# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-08 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0016_remove_uploaderjobexecution_inputs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploaderjobexecution',
            name='executionStart',
            field=models.DateTimeField(null=True, verbose_name='Inicio'),
        ),
    ]
