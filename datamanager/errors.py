# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.errors import FondefVizError


class FileDoesNotExistError(FondefVizError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'El archivo seleccionado no existe'
        super(FileDoesNotExistError, self).__init__(450, message)


class ThereIsPreviousJobUploadingTheFileError(FondefVizError):
    """ It raises when user tries to upload a file which is assigned to enqueued job """

    def __init__(self):
        message = 'El archivo está siendo cargado por otra tarea. Debe esperar a que termine o cancelarla'
        title = 'Advertencia'
        type = 'warning'
        super(ThereIsPreviousJobUploadingTheFileError, self).__init__(451, message, title, type)


class IndexWithDocumentError(FondefVizError):
    """ It raises when user tries to upload a file which has documents already in the index """

    def __init__(self):
        message = 'Existen documentos asociados al archivo en elasticsearch, eliminelos antes de volver a intentar esta acción',
        super(IndexWithDocumentError, self).__init__(452, message)


class BadFormatDocumentError(FondefVizError):
    """ It raises when user send a file without extension """

    def __init__(self):
        message = 'El nombre del archivo seleccionado tiene un formato incorrecto',
        super(BadFormatDocumentError, self).__init__(453, message)


class ThereIsNotActiveJobError(FondefVizError):
    """ It raises when user try to cancel a job that does not exist """

    def __init__(self):
        message = 'No hay tareas de carga para cancelar',
        title = 'Información'
        message_type = 'info'
        super(ThereIsNotActiveJobError, self).__init__(454, message, title, message_type)