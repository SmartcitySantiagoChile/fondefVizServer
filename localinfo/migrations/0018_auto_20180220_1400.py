# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-20 17:00


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0017_auto_20180216_1118'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timeperiod',
            old_name='transantiagoPeriod',
            new_name='authorityPeriodName',
        ),
    ]
