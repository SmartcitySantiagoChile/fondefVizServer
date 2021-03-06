# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-30 21:36


from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0027_auto_20180326_0207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporterjobexecution',
            name='file',
            field=models.FileField(null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/downloads', location=b'D:\\PycharmProjects\\fondefVizServer\\media\\files'), upload_to='zip/', verbose_name='Archivo'),
        ),
        migrations.AlterField(
            model_name='exporterjobexecution',
            name='query',
            field=models.TextField(verbose_name='Consulta a elasticsearch'),
        ),
        migrations.AlterField(
            model_name='exporterjobexecution',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]
