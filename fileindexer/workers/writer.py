import datetime
import gevent
import time

from fileindexer.backends.whoosh_index import WhooshIndex

class Writer(gevent.Greenlet):
    def __init__(self, logger, p_writeq, lock, limit=250):
        gevent.Greenlet.__init__(self)
        self.__l = logger
        self.__q = p_writeq
        self.__lock = lock
        self.__limit = limit
        self.stop = False
        self.__wi = WhooshIndex(logger)
        self.start()

    def flush_buffer(self, buff):
        writer = self.__wi.idx.writer()
        for doc in buff:
            writer.add_document(**doc)
        writer.commit()

    def _run(self):
        self.__l.debug('[writer greenlet]: Starting writer')
        buff = []
        buff_cnt = 0
        while True:
           try:
               meta = self.__q.get()
               if buff_cnt >= self.__limit:
                   self.__l.debug('[writer greenet]: flushing write queue (qsize: %s)' % self.__q.qsize())
                   self.flush_buffer(buff)
                   buff = []
                   buff_cnt = 0
               else:
                   for k,v in meta.items():
                       if k in ['atime', 'ctime', 'mtime']:
                           meta[k] = datetime.datetime.fromtimestamp(v)
                       else:
                           meta[k] = unicode(v)
                   buff.append(meta)
                   buff_cnt += 1
           except gevent.queue.Empty:
               if len(buff) > 0:
                   self.flush_buffer(buff)
               time.sleep(1.0)
        self.__l.debug('[writer greenlet]: Writer stopping')
