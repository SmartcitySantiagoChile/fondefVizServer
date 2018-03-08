# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

import os


class DataSourcePath(models.Model):
    GENERAL = 'general'
    OD_BY_ROUTE = 'odbyroute'
    STOP = 'stop'
    SHAPE = 'shape'
    TRIP = 'trip'
    SPEED = 'speed'
    PROFILE = 'profile'
    """ where i have to check for new files """
    # path to data source
    path = models.CharField("Ruta", max_length=200)
    # Patter of file which has to be searching in the path
    filePattern = models.CharField("Patrón de archivo", max_length=100)
    # Id uses to identify path
    code = models.CharField("código", max_length=50)
    # last time record was updated
    timeStamp = models.DateTimeField("Última actualización", default=timezone.now)

    def __unicode__(self):
        return os.path.join(self.path, self.filePattern)

    class Meta:
        verbose_name = 'Orígen de archivo de carga'
        verbose_name_plural = 'Orígenes de archivos de carga'


class DataSourceFile(models.Model):
    """ record to save data of each file found it """
    # file name found it in one of data source path
    fileName = models.CharField("Nombre de archivo", max_length=200, null=False, unique=True)
    dataSourcePath = models.CharField(max_length=200)
    discoverAt = models.DateTimeField("Primera vez encontrado", null=False)
    lines = models.IntegerField(default=0)

    def get_dict(self):
        """ dictionary of record """
        file_dict = {
            "name": self.fileName,
            "path": self.dataSourcePath,
            "discoverAt": self.discoverAt,
            "lines": self.lines,
            "id": self.id
        }

        return file_dict


class JobExecution(models.Model):
    """ record about async execution """
    jobId = models.UUIDField("Identificador de trabajo", null=False)
    EXPORTER = 'exporter'
    UPLOADER = 'uploader'
    TYPE_CHOICES = (
        (EXPORTER, "Carga de datos"),
        (UPLOADER, "Descarga de datos"),
    )
    type = models.CharField("Tipo", max_length=10, choices=TYPE_CHOICES)
    # time when execution started
    executionStart = models.DateTimeField("Inicio")
    # time when execution finished
    executionEnd = models.DateTimeField("Fin", null=True)
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELED = 'canceled'
    STATUS_CHOICES = (
        (RUNNING, "cargando datos a elastic search"),
        (FINISHED, "Finalización exitosa"),
        (FAILED, "Finalización con error"),
        (CANCELED, "Cancelado por usuario"),
    )
    # state of execution
    status = models.CharField("Estado", max_length=10, choices=STATUS_CHOICES)
    # inputs to job
    inputs = models.TextField("Parámetros de llamada", max_length=500, null=True)
    # for stack trace
    errorMessage = models.TextField("Mensaje de error", max_length=500, null=True)