
import gevent
import gevent.queue
import multiprocessing

from fileindexer.workers.whoosh_writer import WhooshWriter

class WhooshManager(multiprocessing.Process):
    def __init__(self, logger, write_queue):
        multiprocessing.Process.__init__(self)
        self.__l = logger
        self.__wq = write_queue
        self.__wwq = gevent.queue.Queue()

    def query(self, q):
        pass

    def run(self):
        self.__l.debug('Starting WhooshWorkerManager process')

        self.__wwq = gevent.queue.Queue()

        workers = []
        write_worker = WhooshWriter(self.__l, self.__wwq)
        write_worker.start()

        workers.append(write_worker)

        while not self.stop:
            meta = self.__wq.get()
            self.__wwq.put_nowait(meta)

        gevent.joinall(workers)


if __name__ == '__main__':
    pass
