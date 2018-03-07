# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

import os


class DataSourcePath(models.Model):
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

    def getDict(self):
        """ dictionary of record """
        fileDict = {
            "name": self.fileName,
            "path": self.dataSourcePath,
            "discoverAt": self.discoverAt,
            "lines": self.lines,
            "id": self.id
        }

        return fileDict


class DataSourceFileExecutionHistory(models.Model):
    """ history of upload action for each file recorded on data source file model """
    fileName = models.ForeignKey(DataSourceFile, on_delete=models.CASCADE)
    # time when execution started
    executionStart = models.DateTimeField("Inicio")
    # time when execution finished
    executionEnd = models.DateTimeField("Fin", null=True)
    RUNNING = "running"
    FINISHED_WITH_ERROR = "error"
    FINISHED_WITHOUT_ERROR = "ok"
    STATE_CHOICES = (
        (RUNNING, "cargando datos a elastic search"),
        (FINISHED_WITHOUT_ERROR, "Finalización exitosa"),
        (FINISHED_WITH_ERROR, "Finalización con error"),
    )
    # state of execution
    state = models.CharField("Razón de termino", max_length=30, choices=STATE_CHOICES)
    # to save error messages
    message = models.TextField("Mensaje de error", max_length=500, null=True)
