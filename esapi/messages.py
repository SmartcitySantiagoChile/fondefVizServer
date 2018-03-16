# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.errors import format_date


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


class SpeedVariationWithLessDaysMessage(GenericUserMessage):
    """ message to show days used in speed variation  """

    def __init__(self, days_number, operation_program_date):
        message = 'El cálculo se ha realizado con los {0} días previos debido a que existe un cambio en el programa ' \
                  'de operación el día {1} <br/>Por defecto la plataforma usa los 31 días previos'.format(
            days_number, format_date(operation_program_date))
        title = 'Información'
        message_type = 'info'
        super(SpeedVariationWithLessDaysMessage, self).__init__(250, message, title, message_type)
