# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.errors import GenericError


class FileDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'El archivo seleccionado no existe'
        super(FileDoesNotExist, self).__init__(450, message)

class ThereIsPreviousJobUploadingTheFile(GenericError):
    """ It raises when user tries to upload a file which is assigned to enqueued job """

    def __init__(self):
        message = 'El archivo está siendo subido por otra tarea. Debe esperar a que termine'
        title = 'Advertencia'
        type = 'warning'
        super(ThereIsPreviousJobUploadingTheFile, self).__init__(451, message, title, type)
