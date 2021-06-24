from esapi.messages import GenericUserMessage


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
        super(DataDeletedSuccessfully, self).__init__(202, message, title, message_type)


class JobCanceledSuccessfully(GenericUserMessage):
    """  """

    def __init__(self):
        message = 'Se ha cancelado la carga del archivo exitosamente'
        title = 'Carga de datos cancelada'
        message_type = 'success'
        super(JobCanceledSuccessfully, self).__init__(203, message, title, message_type)


class DataIsDeleting(GenericUserMessage):
    """  """

    def __init__(self):
        message = 'Los registros están siendo eliminados. Esta eliminación puede tomar tiempo, paciencia.'
        title = 'Datos están siendo eliminados'
        message_type = 'success'
        super(DataIsDeleting, self).__init__(204, message, title, message_type)
