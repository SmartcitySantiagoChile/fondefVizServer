# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-08 14:17


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamanager', '0013_auto_20180308_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploaderJobExecution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jobId', models.UUIDField(null=True, verbose_name='Identificador de trabajo')),
                ('type', models.CharField(choices=[('exporter', 'Carga de datos'), ('uploader', 'Descarga de datos')], max_length=10, verbose_name='Tipo')),
                ('enqueueTimestamp', models.DateTimeField(verbose_name='Encolado')),
                ('executionStart', models.DateTimeField(verbose_name='Inicio')),
                ('executionEnd', models.DateTimeField(null=True, verbose_name='Fin')),
                ('status', models.CharField(choices=[('enqueued', 'Encolado, esperando para ejecutar'), ('running', 'cargando datos a elastic search'), ('finished', 'Finalizaci\xf3n exitosa'), ('failed', 'Finalizaci\xf3n con error'), ('canceled', 'Cancelado por usuario')], max_length=10, verbose_name='Estado')),
                ('inputs', models.TextField(max_length=500, null=True, verbose_name='Par\xe1metros de llamada')),
                ('errorMessage', models.TextField(max_length=500, null=True, verbose_name='Mensaje de error')),
            ],
            options={
                'verbose_name': 'Trabajo de carga de datos',
                'verbose_name_plural': 'Trabajos de carga de datos',
            },
        ),
        migrations.RenameModel(
            old_name='DataSourceFile',
            new_name='LoadFile',
        ),
        migrations.DeleteModel(
            name='JobExecution',
        ),
        migrations.AddField(
            model_name='uploaderjobexecution',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datamanager.LoadFile'),
        ),
    ]
