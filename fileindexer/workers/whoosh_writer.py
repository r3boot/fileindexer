
import gevent
import time

#import whoosh.writing

from fileindexer.backends.whoosh_index import WhooshIndex

class WhooshWriter(gevent.Greenlet):
    def __init__(self, logger, wrq, limit=500):
        gevent.Greenlet.__init__(self)
        self.__l = logger
        self.__wrq = wrq
        self.__limit = limit
        self.__wi = WhooshIndex(logger)
        #self.__writer = whoosh.writing.BufferedWriter(self.__wi.idx, period=60, limit=limit)
        self.stop = False

    def __destroy__(self):
        self.stop = True

    def flush_buffer(self, buffer):
        self.__l.debug('Flushing write buffer (%s still in queue)' % self.__wrq.qsize())
        writer = self.__wi.idx.writer()
        for doc in buffer:
            writer.add_document(**doc)
        writer.commit()

    def _run(self):
        self.__l.debug('Starting WhooshWriter greenlet')
        buffer = []
        buffer_cnt = 0
        while not self.stop:
            try:
                meta = self.__wrq.get_nowait()
                if buffer_cnt >= self.__limit:
                    self.flush_buffer(buffer)
                    buffer = []
                    buffer_cnt = 0
                else:
                    buffer.append(meta)
                    buffer_cnt += 1
            except gevent.queue.Empty:
                if len(buffer) > 0:
                    self.flush_buffer(buffer)
                else:
                    time.sleep(0.1)
