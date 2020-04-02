# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-18 15:04


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0003_auto_20170717_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSourceFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DataSourceFileExecutionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RenameModel(
            old_name='DataSource',
            new_name='DataSourcePath',
        ),
    ]
