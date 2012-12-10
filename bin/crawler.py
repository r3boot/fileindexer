#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import os
import requests
import sys
import threading
import time

import whoosh.index
import whoosh.fields

__description__ = 'Add description'

_d_debug = False

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

class WhooshBackend:
    def __init__(self, logger):
        self.__l = logger
        self.schema = whoosh.fields.Schema(
            filename=whoosh.fields.TEXT(stored=True),
            atime=whoosh.fields.DATETIME(stored=True),
            ctime=whoosh.fields.DATETIME(stored=True),
            parent=whoosh.fields.TEXT(stored=True),
            gid=whoosh.fields.NUMERIC(stored=True),
            mode=whoosh.fields.NUMERIC(stored=True),
            mtime=whoosh.fields.DATETIME(stored=True),
            is_dir=whoosh.fields.BOOLEAN(stored=True),
            size=whoosh.fields.NUMERIC(stored=True),
            uid=whoosh.fields.NUMERIC(stored=True)
        )
        self.ix = whoosh.index.create_in("/tmp/fileindex", self.schema)

        self.__lock = False

    def add(self, *args, **kwargs):
        while self.__lock:
            time.sleep(1.0)

        self.__lock = True
        writer = self.ix.writer()
        writer.add_document(**kwargs)
        writer.commit()
        self.__lock = False

class Crawler(threading.Thread):
    def __init__(self, logger, wb, url):
        threading.Thread.__init__(self)
        self.__l = logger
        self.__wb = wb
        self.url = url
        self.setDaemon(True)
        self.__t_start = datetime.datetime.now()
        self.__s = requests.session()

    def __request(self, method, path):
        response = {}
        url = '%s%s' % (self.url, path)
        print(url)
        r = None
        try:
            if method == 'get':
                r = self.__s.get(url)
            elif method == 'post':
                r = self.__s.post(url)
            elif method == 'delete':
                r = self.__s.delete(url)
            else:
                self.__l.error('Invalid request method')
        except requests.exceptions.ConnectionError, e:
            r = False
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        except ValueError, e:
            r = False
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        finally:
            if r and r.status_code == 200:
                response['result'] = True
                response['data'] = r.content
            else:
                response['result'] = False
                response['message'] = 'Request failed'

        return response

    def fetch(self, parent='', path=''):
        idx = os.path.join(parent, path, '00INDEX')
        if not idx.startswith('/'):
            idx = '/' + idx

        response = self.__request(method='get', path=idx)
        if response['result']:
            for line in response['data'].split('\n'):
                if not '\t' in line:
                    continue
                (filename, raw_meta) = line.split('\t')
                meta = json.loads(raw_meta)
                meta['filename'] = filename
                self.__wb.add(meta)

                if meta['is_dir']:
                    if parent == '':
                        self.fetch(path, filename)
                    else:
                        self.fetch(parent + '/' + path, filename)
        else:
            print(response['message'])

    def run(self):
        self.__l.debug('Starting crawler for %s' % self.url)
        self.fetch()


def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('url', metavar='URL', type=str,
        nargs='+', help='URL to crawl')

    args = parser.parse_args()

    logger = logging.getLogger('main')
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)

    console_logger = logging.StreamHandler()
    console_logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)

    logger.debug('logging at %s' % ll2str[log_level])

    wb = WhooshBackend(logger)

    crawlers = []
    for url in args.url:
        crawler = Crawler(logger, wb, url)
        crawler.start()
        crawlers.append(crawler)

    for crawler in crawlers:
        crawler.join()

    return

if __name__ == '__main__':
    sys.exit(main())
