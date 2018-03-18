import logging
from gevent import Greenlet


log = logging.getLogger('submit_queue')


class SubmitWorker(Greenlet):
    def __init__(self, queue):
        super(SubmitWorker, self).__init__()
        self.queue = queue
        self.submitted = 0

    def _run(self):
        while True:
            try:
                submit = self.queue.get_submit()
                submit.send()
                self.submitted += 1
            except Exception:
                log.exception('Submit worker caught exception and skipped submit without notifying user')