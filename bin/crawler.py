#!/usr/bin/env python

import Queue
import argparse
import datetime
import json
import logging
import os
import requests
import sys
import threading
import time

__description__ = 'Add description'

_d_debug = False
_d_backend = 'http://127.0.0.1:5423/idx'
_d_apikey = False

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

class RequestBuffer(threading.Thread):
    def __init__(self, logger, backend, apikey):
        threading.Thread.__init__(self)
        self.__l = logger
        self.__b = backend
        self.__k = apikey
        self.q = Queue.Queue()
        self.stop = False
        self.setDaemon(True)
        self.__s = requests.session()
        self.start()

    def __destroy__(self):
        self.q.join()
        self.stop = True

    def __serialize(self, data):
        return json.dumps(data)

    def __request(self, meta):
        response = {}
        r = None
        payload = self.__serialize(meta)
        auth = requests.auth.HTTPBasicAuth('_server', self.__k)
        try:
            r = self.__s.post(self.__b, data=payload, auth=auth)
        except requests.exceptions.ConnectionError, e:
            r = False
            self.__l.error('Request failed: %s' % e)
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        except ValueError, e:
            r = False
            self.__l.error('Request failed: %s' % e)
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        finally:
            if r and r.status_code == 200:
                response['result'] = True
                response['data'] = r.json
            else:
                self.__l.error('Request failed')
                response['result'] = False
                response['message'] = 'Request failed'

        return response

    def run(self):
        self.__l.debug('Starting request buffer thread (%s)' % self.__b)
        batch = []
        batch_cnt = 0
        while not self.stop:
            if self.stop:
                self.__l.info('Waiting for request queue to empty')
                while not self.q.empty():
                    self.__l.debug('qsize: %s' % self.q.qsize())
                    meta = self.q.get()
                    self.__request(meta)
                break

            while not self.q.empty():
                meta = self.q.get()
                batch.append(meta)
                batch_cnt += 1

                if batch_cnt >= 5:
                    self.__request(batch)
                    batch = []
                    batch_cnt = 0
            self.__request(batch)

            time.sleep(0.1)

class Crawler(threading.Thread):
    def __init__(self, logger, request_buffer, url):
        threading.Thread.__init__(self)
        self.__l = logger
        self.__b = request_buffer
        self.url = url
        self.__s = requests.session()
        self.setDaemon(True)
        self.__t_start = datetime.datetime.now()

    def __request(self, method, path):
        response = {}
        url = '%s%s' % (self.url, path)
        self.__l.debug('Parsing %s' % url)
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
                if parent == '':
                    meta['url'] = '%s/%s' % (self.url, os.path.join(path, filename))
                else:
                    meta['url'] = '%s/%s' % (self.url, os.path.join(parent, path, filename))
                self.__b.q.put(meta)

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

    parser.add_argument('--backend', dest='backend', action='store',
        default=_d_backend, help='URL for backend')
    parser.add_argument('--apikey', dest='apikey', action='store',
        default=_d_apikey, help='API key for backend')

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

    rb = RequestBuffer(logger, args.backend, args.apikey)

    crawlers = []
    for url in args.url:
        crawler = Crawler(logger, rb, url)
        crawler.start()
        crawlers.append(crawler)

    for crawler in crawlers:
        crawler.join()

    rb.stop = True
    rb.join()

    return

if __name__ == '__main__':
    sys.exit(main())
