# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-05 22:28


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logapp', '0003_useractions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractions',
            name='method',
            field=models.CharField(max_length=4),
        ),
    ]
