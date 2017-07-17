# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

import os
# Create your models here.


class DataSource(models.Model):
    """ where i have to check for new files """

    # path to data source
    path = models.CharField("Ruta", max_length=200)

    # Patter of file which has to be searching in the path
    patternFile = models.CharField("Patrón de archivo", max_length=100)

    # Id uses to identify path
    code = models.CharField("código", max_length=50)

    # last time record was updated
    timeStamp = models.DateTimeField("Última actualización", default=timezone.now)

    def __unicode__(self):
        return os.path.join(self.path, self.patternFile)

    class Meta:
        verbose_name = u'Orígen de archivo de carga'
        verbose_name_plural = u'Orígenes de archivos de carga'