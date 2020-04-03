# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 18:09


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typeDay', models.CharField(max_length=8)),
                ('transantiagoPeriod', models.CharField(max_length=30)),
                ('initialTime', models.TimeField()),
                ('endTime', models.TimeField()),
            ],
        ),
    ]
