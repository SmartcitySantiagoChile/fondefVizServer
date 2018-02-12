# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ESQueryError(Exception):
    ''' It raises when something goes wrong with elastic search query '''
    DEFAULT_MESSAGE = 'Error al consultar elastic search'
    DEFAULT_TITLE = 'Error'
    MESSAGE_TYPE = 'error'
    CODE = 400

    def __init__(self, code=None, message=None, title=None, messageType=None):
        self.message = message if message else self.DEFAULT_MESSAGE
        self.title = title if title else self.DEFAULT_TITLE
        self.messageType = messageType if messageType else self.MESSAGE_TYPE
        self.code = code if code else self.CODE

    def __str__(self):
        return repr(self.message)

    def getStatusResponse(self):
        ''' message given to end user '''
        response = {}
        response['code'] = self.code
        response['message'] = self.message
        response['title'] = self.title
        response['type'] = self.messageType

        return response


class ESQueryRouteParameterDoesNotExist(ESQueryError):
    ''' It raises when user does not provide params to elastic search query '''

    def __init__(self):
        message = 'Debe indicar la ruta a evaluar'
        super(ESQueryRouteParameterDoesNotExist, self).__init__(401, message)


class ESQueryParametersDoesNotExist(ESQueryError):
    ''' It raises when user does not provide params to elastic search query '''

    def __init__(self):
        message = 'No hay parámetros para realizar la búsqueda'
        super(ESQueryParametersDoesNotExist, self).__init__(402, message)


class ESQueryDateRangeParametersDoesNotExist(ESQueryError):
    ''' It raises when user does not provide params to elastic search query '''

    def __init__(self):
        message = 'Debe proveer parámetros con fecha de inicio y fin para realizar la búsqueda'
        super(ESQueryDateRangeParametersDoesNotExist, self).__init__(402, message)


class ESQueryResultEmpty(ESQueryError):
    ''' It raises when user does not provide params to elastic search query '''

    def __init__(self):
        message = 'La consulta no arrojó resultados'
        title = 'Información'
        messageType = 'info'
        super(ESQueryResultEmpty, self).__init__(403, message, title, messageType)


class ESQueryStopParameterDoesNotExist(ESQueryError):
    ''' It raises when user does not provide params to elastic search query '''

    def __init__(self):
        message = 'Debe indicar el paradero a evaluar (campo Paradero)'
        super(ESQueryStopParameterDoesNotExist, self).__init__(404, message)
