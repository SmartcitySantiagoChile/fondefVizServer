# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-25 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0023_exporterjobexecution_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporterjobexecution',
            name='status',
            field=models.CharField(choices=[('enqueued', 'Encolado'), ('running', 'Cargando datos'), ('finished', 'Finalizaci\xf3n exitosa'), ('failed', 'Finalizaci\xf3n con error'), ('canceled', 'Cancelado por usuario'), ('finished_m', 'Finalizaci\xf3n exitosa')], max_length=10, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='uploaderjobexecution',
            name='status',
            field=models.CharField(choices=[('enqueued', 'Encolado'), ('running', 'Cargando datos'), ('finished', 'Finalizaci\xf3n exitosa'), ('failed', 'Finalizaci\xf3n con error'), ('canceled', 'Cancelado por usuario'), ('finished_m', 'Finalizaci\xf3n exitosa')], max_length=10, verbose_name='Estado'),
        ),
    ]