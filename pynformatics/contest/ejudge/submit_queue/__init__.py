from .queue import SubmitQueue


class DefaultSubmitQueue:
    submit_queue = None

    def queue_submit(self, *args, **kwargs):
        self.submit_queue.put_submit(*args, **kwargs)


_instance = DefaultSubmitQueue()
queue_submit = _instance.queue_submit


def init_submit_queue(settings):
    _instance.submit_queue = SubmitQueue(
        workers=int(settings.get('submit_queue.workers', '2'))
    )
