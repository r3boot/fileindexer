
import gevent

from fileindexer.backends.whoosh_index import WhooshIndex

class WhooshReader(gevent.Greenlet):
    def __init__(self, logger, period=60, limit=1000):
        gevent.Greenlet.__init__(self)
        self.__l = logger
        self.__lock = gevent.coros.BoundedSemaphore(1)
        self.__writeq = gevent.queue.Queue()
        self.wi = WhooshIndex(logger)
        self.stop = False

    def __destroy__(self):
        self.stop = True
