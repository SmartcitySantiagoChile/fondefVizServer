# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-07 14:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logapp', '0005_usersession_usersessionstats'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersessionstats',
            name='total_session_duration',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
