# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.messages import GenericUserMessage


class PasswordUpdatedSuccessfully(GenericUserMessage):
    """  """

    def __init__(self):
        message = 'Tu contraseña ha sido actualizada correctamente!'
        title = 'Éxito'
        message_type = 'success'
        super(PasswordUpdatedSuccessfully, self).__init__(205, message, title, message_type)


class FormError(GenericUserMessage):
    """  """

    def __init__(self, error_list):
        message = 'Por favor corrige los siguientes errores:<ul>{0}</ul>\n'.format(
            "".join(["<li>{0}</li>".format(error_list[key]) for key in error_list]))
        title = 'Error'
        message_type = 'error'
        super(FormError, self).__init__(206, message, title, message_type)
