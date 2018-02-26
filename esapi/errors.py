# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class ESQueryError(Exception):
    """ It raises when something goes wrong with elastic search query """
    DEFAULT_MESSAGE = 'Error al consultar elastic search'
    DEFAULT_TITLE = 'Error'
    MESSAGE_TYPE = 'error'
    CODE = 400

    def __init__(self, code=None, message=None, title=None, messageType=None):
        self.message = message if message else self.DEFAULT_MESSAGE
        self.title = title if title else self.DEFAULT_TITLE
        self.message_type = messageType if messageType else self.MESSAGE_TYPE
        self.code = code if code else self.CODE

    def __str__(self):
        return repr(self.message)

    def get_status_response(self):
        """ message given to end user """
        response = {}
        response['code'] = self.code
        response['message'] = self.message
        response['title'] = self.title
        response['type'] = self.message_type

        return response


class ESQueryRouteParameterDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar la ruta a evaluar'
        super(ESQueryRouteParameterDoesNotExist, self).__init__(401, message)


class ESQueryParametersDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'No hay parámetros para realizar la búsqueda'
        super(ESQueryParametersDoesNotExist, self).__init__(402, message)


class ESQueryDateRangeParametersDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe proveer parámetros con fecha de inicio y fin para realizar la búsqueda'
        super(ESQueryDateRangeParametersDoesNotExist, self).__init__(402, message)


class ESQueryResultEmpty(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'La consulta no arrojó resultados'
        title = 'Información'
        message_type = 'info'
        super(ESQueryResultEmpty, self).__init__(403, message, title, message_type)


class ESQueryStopParameterDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar el paradero a evaluar'
        super(ESQueryStopParameterDoesNotExist, self).__init__(404, message)


class ESQueryStopPatternTooShort(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'El patrón indicado es demasiado corto'
        super(ESQueryStopPatternTooShort, self).__init__(405, message)


class ESQueryOriginZoneParameterDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar zona(s) de origen'
        super(ESQueryOriginZoneParameterDoesNotExist, self).__init__(406, message)


class ESQueryExistTwoShapesInTimePeriod(ESQueryError):
    """ It raises when user ask for a route shape with a time windows that contains more than one """

    def __init__(self):
        message = 'El período indicado contiene más de una ruta.'
        super(ESQueryExistTwoShapesInTimePeriod, self).__init__(407, message)


class ESQueryDestinationZoneParameterDoesNotExist(ESQueryError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar zona(s) de destino'
        super(ESQueryDestinationZoneParameterDoesNotExist, self).__init__(408, message)


class ESQueryStagesEmpty(ESQueryError):
    """ It raises when user does not provide stages to filter elastic search query """

    def __init__(self):
        message = 'Debe seleccionar las etapas que desea visualizar'
        title = 'Información'
        message_type = 'info'
        super(ESQueryStagesEmpty, self).__init__(409, message, title, message_type)


class ESQueryOperatorParameterDoesNotExist(ESQueryError):
    """ It raises when user does not have permission over operators """

    def __init__(self):
        message = 'No tiene permisos para preguntar por algún operador. Por favor contáctese con el administrador'
        super(ESQueryOperatorParameterDoesNotExist, self).__init__(410, message)
