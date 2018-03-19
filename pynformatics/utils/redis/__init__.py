from redis import StrictRedis


class RedisWrapper:
    def __init__(self):
        self.redis = None

    def init_redis(self, settings):
        self.redis = StrictRedis(
            host=settings['redis.host'],
            port=settings['redis.port'],
            db=settings['redis.db']
        )

    def __getattr__(self, item):
        return getattr(self.redis, item)


redis = RedisWrapper()
init_redis = redis.init_redis
