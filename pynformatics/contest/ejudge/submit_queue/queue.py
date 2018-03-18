import logging
import pickle

from .submit import Submit
from .worker import SubmitWorker
from pynformatics.utils.redis.queue import RedisQueue


log = logging.getLogger('submit_queue')

REDIS_QUEUE_KEY = 'submit.queue'


class SubmitQueue(RedisQueue):
    def __init__(self, workers, key=REDIS_QUEUE_KEY):
        super(SubmitQueue, self).__init__(key)
        self.total_in = 0
        self.workers = [
            SubmitWorker(self)
            for _ in range(workers)
        ]
        for worker in self.workers:
            worker.start()

    @property
    def total_out(self):
        return sum([worker.submitted for worker in self.workers])

    def put_submit(self, user, problem, file, language_id, ejudge_url, statement=None):
        submit = Submit(
            user_id=user.id,
            file=file,
            language_id=language_id,
            ejudge_contest_id=problem.ejudge_contest_id,
            ejudge_problem_id=problem.problem_id,
            ejudge_user_login=user.login,
            ejudge_user_password=user.password,
            ejudge_url=ejudge_url,
            statement_id=getattr(statement, 'id', None),
        )
        self.put(submit.encode())

        self.total_in += 1
        log.info('Current size: %s. Total submitted: %s.', self.total_in - self.total_out, self.total_out)

    def get_submit(self):
        encoded_submit = self.get(blocking=True)
        return Submit.decode(encoded_submit)
