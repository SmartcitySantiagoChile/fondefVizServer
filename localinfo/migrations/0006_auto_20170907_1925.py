# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-07 22:25


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0005_halfhour_longname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='halfhour',
            name='longName',
            field=models.CharField(max_length=15),
        ),
    ]
