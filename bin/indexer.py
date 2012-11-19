#!/usr/bin/env python

import argparse
import base64
import hashlib
import json
import logging
import mimetypes
import os
import requests
import sys
import threading

__description__ = 'Add description'

_d_debug = False
_d_host = '127.0.0.1'
_d_port = '5423'

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

class Indexer(threading.Thread):
    def __init__(self, logger, api, path):
        threading.Thread.__init__(self)
        self.__l = logger
        self.api = api
        self.path = path
        self.setDaemon(True)

    def run(self):
        self.index(self.path)

    def index(self, path):
        for (root, dirs, files) in os.walk(path):
            for f in files:
                full_path = '%s/%s' % (root, f)
                self.add(full_path.encode('UTF-8'))

    def add(self, path):
        meta = {}
        try:
            stat = os.stat(path)
        except OSError, e:
            self.__l.error(e)
            return

        meta['path'] = path
        meta['path_sha1'] = hashlib.sha1(path).hexdigest()
        meta['mode'] = stat.st_mode
        meta['uid'] = stat.st_uid
        meta['gid'] = stat.st_gid
        meta['size'] = stat.st_size
        meta['atime'] = stat.st_atime
        meta['mtime'] = stat.st_mtime
        meta['ctime'] = stat.st_ctime
        try:
            meta['mime'] = mimetypes.guess_type(path)[0]
        except:
            meta['mime'] = False

        self.api.add_file(meta)

class API():
    def __init__(self, logger, host, port):
        self.__l = logger
        self.__host = host
        self.__port = port

    def __serialize(self, data):
        return base64.b64encode(json.dumps(data))

    def __deserialize(self, data):
        return json.loads(base64.b64decode(data))

    def __get_url(self, cmd, item=None, value=None):
        if item and value:
            return 'http://%s:%s/%s/%s/%s' % (self.__host, self.__port, cmd, item, value)
        elif item:
            return 'http://%s:%s/%s/%s' % (self.__host, self.__port, cmd, item)
        else:
            return 'http://%s:%s/%s' % (self.__host, self.__port, cmd)

    def __fetch(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            return self.__deserialize(r.text)

    def is_alive(self):
        url = self.__get_url('ping')
        #data = self.__deserialize(self.__fetch(url))
        data = self.__fetch(url)
        return data == 'pong'

    def cfg_get(self, item):
        url = self.__get_url('cfg/get', item)
        data = self.__fetch(url)
        return data

    def cfg_set(self, item, value):
        url = self.__get_url('cfg/set', item, self.__serialize(value))
        data = self.__fetch(url)
        return data

    def add_file(self, meta):
        url = self.__get_url('file/add', self.__serialize(meta))
        data = self.__fetch(url)
        if data:
            return data

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('-H', dest='host', action='store',
        default=_d_host, help='Host to connect to, defaults to %s' % _d_host)
    parser.add_argument('-P', dest='port', action='store',
        default=_d_port, help='Port to connect to, defaults to %s' % _d_port)

    parser.add_argument('--add-path', dest='add_path', action='store',
        default=False, help='Add path to index')
    parser.add_argument('--list-paths', dest='list_paths', action='store_true',
        default=False, help='Display all indexed paths')

    parser.add_argument('--index', dest='index', action='store_true',
        default=False, help='Index all paths')

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

    api = API(logger, args.host, args.port)
    if api.is_alive():
        logger.debug('Connected to API at %s:%s' % (args.host, args.port))
    else:
        logger.debug('Failed to connect to API at %s:%s' % (args.host, args.port))
        return

    if args.list_paths:
        paths = api.cfg_get('paths')
        if not paths:
            logger.error('No paths found')
            return 1
        print('==> Indexed paths')
        for path in api.cfg_get('paths'):
            print('* %s' % path)
    elif args.add_path:
        paths = api.cfg_get('paths')
        if not paths:
            paths = []
        if args.add_path in paths:
            logger.error('Path already indexed')
            return 1
        paths.append(args.add_path)
        result = api.cfg_set('paths', paths)
        if not result:
            logger.error('Failed to set config.paths')
            return 1
    elif args.index:
        mimetypes.init()
        indexers = []
        paths = api.cfg_get('paths')
        if not paths:
            logger.error('No paths found')
            return 1
        for path in paths:
            logger.debug('Starting thread for %s' % path)
            indexer = Indexer(logger, api, path)
            indexer.start()
            indexers.append(indexer)

        for indexer in indexers:
            indexer.join()

    return

if __name__ == '__main__':
    sys.exit(main())
