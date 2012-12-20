
import multiprocessing
import os
import tempfile
import time

from fileindexer.workers.indexer import indexer
from fileindexer.indexer.index_writer import IndexWriter

class IndexerFeeder:
    def __init__(self, logger, start_paths, indexers=8, reaplimit=1000):
        self.__l = logger
        self.__start_paths = start_paths
        self.__indexers = indexers
        self.__reaplimit = reaplimit
        self.__idxwriter = IndexWriter(logger)
        (fd, self.__fifo) = tempfile.mkstemp()
        self.__fd = os.open(self.__fifo, os.O_WRONLY | os.O_NONBLOCK)
        self.stop = False

    def __destroy__(self):
        if self.__fd:
            os.close(self.__fd)

    def run(self):
        self.__l.debug('Starting IndexerFeeder')

        pool = multiprocessing.Pool(processes=self.__indexers, maxtasksperchild=self.__reaplimit)
        manager = multiprocessing.Manager()
        in_q = manager.Queue()
        out_q = manager.Queue()

        pool.apply_async(indexer, (self.__l.getEffectiveLevel(), in_q, out_q,))

        ## Seed the initial queue
        for path in self.__start_paths:
            in_q.put(path)

        self.__l.debug('before feedback: in_q.qsize: %s; out_q.qsize: %s' % (in_q.qsize(), out_q.qsize()))

        ## Start the feedback loop
        while True:
            path = out_q.get()
            print('received: %s' % path)
            in_q.put(path)

        pool.join()
        self.__l.debug('Stopping IndexerFeeder')
