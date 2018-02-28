from rq import Worker

from rqworkers.datauploader.loadData import upload_file


class UploaderWorker(Worker):
    """ Worker that preloads the necessary imports to upload data """

    def __init__(self, queues, name=None, default_result_ttl=None, connection=None,
                 exc_handler=None, exception_handlers=None, default_worker_ttl=None,
                 job_class=None, queue_class=None):
        super(UploaderWorker, self).__init__(queues, name=name, default_result_ttl=default_result_ttl,
                                             connection=connection, exc_handler=exc_handler,
                                             exception_handlers=exception_handlers,
                                             default_worker_ttl=default_worker_ttl, job_class=job_class,
                                             queue_class=queue_class)
