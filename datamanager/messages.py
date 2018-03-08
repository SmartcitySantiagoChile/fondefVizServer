# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class GenericUserMessage(object):
    """ message for user """
    DEFAULT_MESSAGE = 'generic message'
    DEFAULT_TITLE = 'info'
    MESSAGE_TYPE = 'info'
    CODE = 200

    def __init__(self, code=None, message=None, title=None, message_type=None):
        self.message = message if message else self.DEFAULT_MESSAGE
        self.title = title if title else self.DEFAULT_TITLE
        self.message_type = message_type if message_type else self.MESSAGE_TYPE
        self.code = code if code else self.CODE

    def __str__(self):
        return repr(self.message)

    def get_status_response(self):
        """ message given to end user """
        response = {
            'code': self.code,
            'message': self.message,
            'title': self.title,
            'type': self.message_type
        }

        return response


class JobEnqueued(GenericUserMessage):
    """  """

    def __init__(self):
        message = 'El archivo ha sido encolado para ser cargado en elasticsearch'
        title = 'Archivo encolado'
        message_type = 'success'
        super(JobEnqueued, self).__init__(201, message, title, message_type)


class DataDeletedSuccessfully(GenericUserMessage):
    """  """

    def __init__(self, deleted_doc_number=0):
        message = 'Se han eliminado {0} documentos de elasticsearch existosamente'.format(deleted_doc_number)
        title = 'Datos eliminados'
        message_type = 'success'
        super(DataDeletedSuccessfully, self).__init__(201, message, title, message_type)


class JobCanceledSuccessfully(GenericUserMessage):
    """  """

    def __init__(self):
        message = 'Se ha cancelado la carga del archivo exitosamente'
        title = 'Carga de datos cancelada'
        message_type = 'success'
        super(JobCanceledSuccessfully, self).__init__(201, message, title, message_type)
