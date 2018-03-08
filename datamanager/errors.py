# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.errors import GenericError


class FileDoesNotExistError(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'El archivo seleccionado no existe'
        super(FileDoesNotExistError, self).__init__(450, message)


class ThereIsPreviousJobUploadingTheFileError(GenericError):
    """ It raises when user tries to upload a file which is assigned to enqueued job """

    def __init__(self):
        message = 'El archivo está siendo subido por otra tarea. Debe esperar a que termine'
        title = 'Advertencia'
        type = 'warning'
        super(ThereIsPreviousJobUploadingTheFileError, self).__init__(451, message, title, type)


class IndexWithDocumentError(GenericError):
    """ It raises when user tries to upload a file which has documents already in the index """

    def __init__(self):
        message = 'Existen documentos asociados al archivo en elasticsearch, eliminelos antes de volver a intentar esta acción',
        super(IndexWithDocumentError, self).__init__(452, message)


class BadFormatDocumentError(GenericError):
    """ It raises when user send a file without extension """

    def __init__(self):
        message = 'El nombre del archivo seleccionado tiene un formato incorrecto',
        super(BadFormatDocumentError, self).__init__(453, message)
