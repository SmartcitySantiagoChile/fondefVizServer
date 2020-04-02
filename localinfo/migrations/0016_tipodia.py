# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-16 14:17


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localinfo', '0015_auto_20171218_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('esId', models.IntegerField(unique=True, verbose_name='Identificador')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de d\xeda',
                'verbose_name_plural': 'Tipos de d\xeda',
            },
        ),
    ]
