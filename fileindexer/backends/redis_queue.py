
import redis

class RedisQueue:
    def __init__(self, logger, name):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.__queue = redis.Redis(connection_pool=pool)
        self.__name = name

    def get(self):
        return self.__queue.lpop(self.__name)

    def put(self, item):
        return self.__queue.rpush(self.__name, item)

    def qsize(self):
        return self.__queue.llen(self.__name)

    def empty(self):
        return self.qsize() == 0
