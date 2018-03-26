# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-26 05:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0026_auto_20180326_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporterjobexecution',
            name='fileType',
            field=models.CharField(choices=[('odbyroute', 'Matriz de etapa por servicio'), ('speed', 'Velocidades'), ('trip', 'Viajes'), ('profile', 'Perfil de carga')], default='trip', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exporterjobexecution',
            name='filters',
            field=models.TextField(null=True),
        ),
    ]
