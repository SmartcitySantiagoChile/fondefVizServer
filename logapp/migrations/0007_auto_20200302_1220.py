# Generated by Django 1.11.23 on 2020-03-02 15:20


import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('logapp', '0006_usersessionstats_total_session_duration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersessionstats',
            options={'verbose_name': 'estad\xedsticas de usuario',
                     'verbose_name_plural': 'estad\xedsticas de usuarios'},
        ),
        migrations.AlterField(
            model_name='usersession',
            name='duration',
            field=models.DurationField(verbose_name='Duraci\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersession',
            name='end_time',
            field=models.DateTimeField(verbose_name='Final'),
        ),
        migrations.AlterField(
            model_name='usersession',
            name='start_time',
            field=models.DateTimeField(verbose_name='Inicio'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='avg_session_duration',
            field=models.DurationField(verbose_name='Duraci\xf3n promedio de sesi\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='last_session_timestamp',
            field=models.DateTimeField(verbose_name='Ultima sesi\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='max_session_duration',
            field=models.DurationField(verbose_name='Duraci\xf3n m\xe1xima de sesi\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='min_session_duration',
            field=models.DurationField(verbose_name='Duraci\xf3n m\xednima de sesi\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='session_number',
            field=models.IntegerField(verbose_name='N\xfamero de sesi\xf3n'),
        ),
        migrations.AlterField(
            model_name='usersessionstats',
            name='total_session_duration',
            field=models.DurationField(default=datetime.timedelta(0), verbose_name='Duraci\xf3n total de sesi\xf3n'),
        ),
    ]
