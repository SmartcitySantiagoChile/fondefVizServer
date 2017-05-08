# -*- coding: utf-8 -*-

class ESQueryDoesNotHaveParameters(Exception):
    ''' It raises when user does not provide params to elastic search query '''
    DEFAULT_MESSAGE = 'No hay parámetros para realizar la búsqueda'

    def __init__(self, value = None):
        if value:
            self.value = value 
        else:
            self.value = self.DEFAULT_MESSAGE

    def __str__(self):
        return repr(self.value)

    def getStatusResponse(self):
        ''' message given to end user '''
        response = {}
        response['code'] = 400
        response['message'] = self.value

        return response
