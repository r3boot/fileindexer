
#import gevent
import gevent.pool
import gevent.queue
import gevent.coros
import requests

from fileindexer.workers.crawler import crawler
from fileindexer.workers.writer import Writer

class CrawlerManager:
    def __init__(self, logger, start_urls, crawlers=8):
        self.__l = logger
        self.__start_urls = start_urls
        self.__crawlers = crawlers
        self.__out_q = gevent.queue.Queue()
        self.__write_q = gevent.queue.Queue()
        self.__lock = gevent.coros.Semaphore()
        self.__s = requests.session()
        self.stop = False

    def run(self):
        self.__l.debug('Starting CrawlerManager')

        pool = gevent.pool.Pool(self.__crawlers)
        writer = Writer(self.__l, self.__write_q, self.__lock)

        for url in self.__start_urls:
            pool.spawn(crawler, self.__l, self.__s, url, self.__out_q, self.__lock)

        # Start the feedback loop
        while True:
            results = self.__out_q.get()

            for meta in results:
                if meta['is_dir']:
                    pool.spawn(crawler, self.__l, self.__s, meta['url'], self.__out_q, self.__lock)
                self.__write_q.put(meta)

        pool.join()
        self.__.debug('Waiting for write queue to empty (qsize: %s)' % self.__out_q.qsize())
        writer.join()
        self.__l.debug('Stopping CrawlerManager')
