# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-05 14:03


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0029_auto_20180403_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploaderjobexecution',
            name='wasDeletedAt',
            field=models.DateTimeField(null=True, verbose_name='Eliminado'),
        ),
    ]
