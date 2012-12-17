
import gevent.pool
import gevent.queue
import gevent.coros
import json
import os
import requests
import tempfile
import time

from fileindexer.workers.crawler import crawler
from fileindexer.workers.writer import Writer

class CrawlerFeeder:
    def __init__(self, logger, start_urls, crawlers=8):
        self.__l = logger
        self.__start_urls = start_urls
        self.__crawlers = crawlers
        self.__out_q = gevent.queue.Queue()
        self.__write_q = gevent.queue.Queue()
        self.__s = requests.session()
        (fd, self.__fifo) = tempfile.mkstemp()
        self.__fd = os.open(self.__fifo, os.O_WRONLY | os.O_NONBLOCK)
        self.stop = False

    def __destroy__(self):
        if self.__fd:
            os.close(self.__fd)

    def run(self):
        self.__l.debug('Starting CrawlerManager')

        pool = gevent.pool.Pool(self.__crawlers)

        writer = Writer(self.__l, self.__fifo)
        writer.start()

        ## Seed initial pool
        for url in self.__start_urls:
            pool.spawn(crawler, self.__l, self.__s, url, self.__out_q)

        ## Wait for out_q queue to fill
        i = 0
        has_results = False
        while not has_results:
            if i == 30:
                self.__l.debug('No results found')
                break

            if self.__out_q.qsize() > 0:
                has_results = True
                break
            else:
                time.sleep(0.1)
                i += 1

        ## Start the feedback loop
        while has_results:
            if self.__out_q.qsize() == 0:
                has_results = False

            results = self.__out_q.get()

            for meta in results:
                if meta['is_dir']:
                    pool.spawn(crawler, self.__l, self.__s, meta['url'], self.__out_q)
                os.write(self.__fd, '%s\n' % json.dumps(meta))

        pool.join()
        os.close(self.__fd)
        writer.join()
        self.__l.debug('Stopping CrawlerManager')
