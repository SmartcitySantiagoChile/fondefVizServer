# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-05 18:19
from __future__ import unicode_literals

import datamanager.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0030_uploaderjobexecution_wasdeletedat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporterjobexecution',
            name='file',
            field=models.FileField(null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/downloads', location=b'C:\\Users\\cephei\\PycharmProjects\\fondefVizServer\\media\\files'), upload_to=datamanager.models.get_upload_path, verbose_name='Archivo'),
        ),
    ]
