# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-18 16:07


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0005_auto_20170718_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasourcefile',
            name='fileName',
            field=models.CharField(max_length=200, unique=True, verbose_name='Nombre de archivo'),
        ),
    ]
