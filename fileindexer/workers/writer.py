import datetime
import json
import multiprocessing
import os

from fileindexer.backends.whoosh_index import WhooshIndex

class Writer(multiprocessing.Process):
    def __init__(self, logger, fifo, limit=1000):
        multiprocessing.Process.__init__(self)
        self.__l = logger
        self.__fifo = fifo
        self.__limit = limit
        self.stop = False
        self.__wi = WhooshIndex(logger)
        self.__fd = os.open(self.__fifo, os.O_RDONLY)

    def __destroy__(self):
        if self.__fd:
            os.close(self.__fd)

    def flush_buffer(self, buff):
        writer = self.__wi.idx.writer()
        for doc in buff:
            writer.add_document(**doc)
        writer.commit()

    def run(self):
        self.__l.debug('[writer process]: Starting writer')
        raw_buff = ''
        buff = []
        buff_cnt = 0
        while True:
            c = os.read(self.__fd, 1)
            if c != '\n':
                raw_buff += c
            else:
                meta = json.loads(raw_buff)
                raw_buff = ''
                if buff_cnt >= self.__limit:
                    self.__l.debug('[writer process]: flushing write queue')
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
        self.__l.debug('[writer process]: Writer stopping')

if __name__ == '__main__':
    pass
