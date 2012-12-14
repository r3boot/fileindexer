
import gevent
import gevent.queue

from fileindexer.workers.whoosh_writer import WhooshWriter

class WhooshWorkerManager(gevent.Greenlet):
    def __init__(self, logger):
        gevent.Greenlet.__init__(self)
        self.__l = logger
        self.__wq = gevent.queue.Queue()

    def add_document(self, meta):
        try:
            self.__wq.put_nowait(meta)
        except gevent.queue.Full:
            self.__l.warn('Queue is full')

    def query(self, q):
        pass

    def _run(self):
        self.__l.debug('Starting WhooshWorkerManager greenlet')

        workers = []
        ww = WhooshWriter(self.__l, self.wq)
        ww.start()
        workers.append(ww)
        gevent.joinall(workers)
