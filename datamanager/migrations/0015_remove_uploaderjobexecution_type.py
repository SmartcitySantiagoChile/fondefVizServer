# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-08 15:46


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0014_auto_20180308_1117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploaderjobexecution',
            name='type',
        ),
    ]
