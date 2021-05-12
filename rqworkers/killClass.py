from rq.worker import Worker
from rq.job import Job
from django_rq.queues import DjangoRQ

from threading import Thread

import os
import time
import signal

kill_key = "rq:jobs:kill"


class KillJob(Job):
    def kill(self):
        """ Force kills the current job causing it to fail """
        if self.is_started:
            self.connection.sadd(kill_key, self.get_id())

    def _execute(self):
        def check_kill(conn, job_id, interval=1):
            """
            :param conn: redis connection
            :param job_id: job identifier
            :param interval: seconds to wait before check again, default 1 second
            :return: None
            """
            while True:
                res = conn.srem(kill_key, job_id)
                if res > 0:
                    os.kill(os.getpid(), signal.SIGKILL)
                time.sleep(interval)

        t = Thread(target=check_kill, args=(self.connection, self.get_id()))
        t.start()

        return super(KillJob, self)._execute()


class KillQueue(DjangoRQ):
    job_class = KillJob


class KillWorker(Worker):
    queue_class = KillQueue
    job_class = KillJob
