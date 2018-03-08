# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class GenericError(Exception):
    """ It raises when something goes wrong with elastic search query """
    DEFAULT_MESSAGE = 'Error al consultar elastic search'
    DEFAULT_TITLE = 'Error'
    MESSAGE_TYPE = 'error'
    CODE = 400

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


class ESQueryRouteParameterDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar la ruta a evaluar'
        super(ESQueryRouteParameterDoesNotExist, self).__init__(401, message)


class ESQueryParametersDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'No hay parámetros para realizar la búsqueda'
        super(ESQueryParametersDoesNotExist, self).__init__(402, message)


class ESQueryDateRangeParametersDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe proveer parámetros con fecha de inicio y fin para realizar la búsqueda'
        super(ESQueryDateRangeParametersDoesNotExist, self).__init__(402, message)


class ESQueryResultEmpty(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'La consulta no arrojó resultados'
        title = 'Información'
        message_type = 'info'
        super(ESQueryResultEmpty, self).__init__(403, message, title, message_type)


class ESQueryStopParameterDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar el paradero a evaluar'
        super(ESQueryStopParameterDoesNotExist, self).__init__(404, message)


class ESQueryStopPatternTooShort(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'El patrón indicado es demasiado corto'
        super(ESQueryStopPatternTooShort, self).__init__(405, message)


class ESQueryOriginZoneParameterDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar zona(s) de origen'
        super(ESQueryOriginZoneParameterDoesNotExist, self).__init__(406, message)


class ESQueryExistTwoShapesInTimePeriod(GenericError):
    """ It raises when user ask for a route shape with a time windows that contains more than one """

    def __init__(self):
        message = 'El período indicado contiene más de una ruta.'
        super(ESQueryExistTwoShapesInTimePeriod, self).__init__(407, message)


class ESQueryDestinationZoneParameterDoesNotExist(GenericError):
    """ It raises when user does not provide params to elastic search query """

    def __init__(self):
        message = 'Debe indicar zona(s) de destino'
        super(ESQueryDestinationZoneParameterDoesNotExist, self).__init__(408, message)


class ESQueryStagesEmpty(GenericError):
    """ It raises when user does not provide stages to filter elastic search query """

    def __init__(self):
        message = 'Debe seleccionar las etapas que desea visualizar'
        title = 'Información'
        message_type = 'info'
        super(ESQueryStagesEmpty, self).__init__(409, message, title, message_type)


class ESQueryOperatorParameterDoesNotExist(GenericError):
    """ It raises when user does not have permission over operators """

    def __init__(self):
        message = 'No tiene permisos para preguntar por algún operador. Por favor contáctese con el administrador'
        super(ESQueryOperatorParameterDoesNotExist, self).__init__(410, message)


class ESQueryOperationProgramDoesNotExist(GenericError):
    """ It raises when user ask for a route stop list with a date that it does not have stop list declared before """

    def __init__(self, asked_date, available_days):
        available_days = map(lambda x: '<li>{0}</li>'.format(x), available_days)
        available_days = reduce(lambda x, y: '{0}{1}'.format(x, y), available_days, '')
        first_paragraph = 'No existe programa de operación previo a la fecha señalada ({0})<br />'.format(asked_date)
        second_paragraph = 'Los programas de operación disponible son: <br /><ul>{0}</ul>'.format(available_days)
        message = '{0}{1}'.format(first_paragraph, second_paragraph)
        super(ESQueryOperationProgramDoesNotExist, self).__init__(411, message)


class ESQueryThereIsMoreThanOneOperationProgram(GenericError):
    """ It raises when user ask for a route stop list with a date that it does not have stop list declared before """

    def __init__(self, start_date, end_date, days_between):
        days_between = map(lambda x: '<li>{0}</li>'.format(x), days_between)
        days_between = reduce(lambda x, y: '{0}{1}'.format(x, y), days_between, '')
        title = 'Existe más de un programa de operación entre {0} y {1}<br />'.format(
            start_date, end_date)
        first_paragraph = 'Programas de operación presentes en el período consultado: <br /><ul>{0}</ul>'.format(
            days_between)
        second_paragraph = '<b>Consejo:</b><br />Puede existir a lo más un programa de operación en el período de consulta y debe ser igual a la fecha inicial<br />'
        message = '{0}{1}'.format(first_paragraph, second_paragraph)
        super(ESQueryThereIsMoreThanOneOperationProgram, self).__init__(412, message, title=title)
