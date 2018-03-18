from pynformatics.utils.redis import redis


class RedisQueue:
    def __init__(self, key):
        self.key = key

    def put(self, value):
        return redis.rpush(self.key, value)

    def get(self, blocking=False):
        if blocking:
            item = redis.blpop(self.key)[1]
        else:
            item = redis.lpop(self.key)
            if item:
                item = item[1]
        return item
