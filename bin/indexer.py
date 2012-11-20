#!/usr/bin/env python

import argparse
import base64
import datetime
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
        self.__t_start = datetime.datetime.now()

    def run(self):
        num_files = self.index(self.path)
        t_end = datetime.datetime.now()
        t_total = t_end - self.__t_start
        self.__l.debug('Finished indexing %s in %s (%s files)' % (self.path, t_total, num_files))

    def index(self, path):
        num_files = 0
        for (parent, dirs, files) in os.walk(path):
            for f in files:
                num_files += 1
                full_path = '%s/%s' % (parent, f)
                self.add(parent, full_path.encode('UTF-8'))
        return num_files

    def add(self, parent, path):
        meta = {}
        try:
            stat = os.stat(path)
        except OSError, e:
            self.__l.error(e)
            return

        meta['path'] = path
        meta['_id'] = hashlib.sha1(path).hexdigest()
        meta['parent'] = parent
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
        self.__uri = 'http://%s:%s' % (host, port)
        self.__s = requests.session()

    def __serialize(self, data):
        return base64.b64encode(json.dumps(data))

    def __request(self, method, path, payload={}):
        response = {}
        url = self.__uri + path
        if payload:
            payload = self.__serialize(payload)
        try:
            if method == 'get':
                r = self.__s.get(url)
            elif method == 'post':
                r = self.__s.post(url, data=payload)
            else:
                self.__l.error('Invalid request method')
        except requests.exceptions.ConnectionError, e:
            r = False
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        finally:
            if r and r.status_code == 200:
                response = r.json
            else:
                response['result'] = False
                response['message'] = 'Request failed'

        return response

    def ping(self):
        response = self.__request(method='get', path='/ping')
        return response['result']

    def get_config(self):
        response = self.__request(method='get', path='/config')
        if response['result']:
            return response['config']
        else:
            self.__l.error(response['message'])
            return {}

    def set_config(self, key, value):
        payload = {'value': value}
        response = self.__request(method='post', path='/config/%s' % key, payload=payload)
        return response['result']

    def add_file(self, meta):
        payload = {'meta': meta}
        response = self.__request(method='post', path='/files', payload=payload)
        return response['result']

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
    parser.add_argument('--del-path', dest='del_path', action='store',
        default=False, help='Remove path from index')
    parser.add_argument('--list-paths', dest='list_paths', action='store_true',
        default=False, help='Display all indexed paths')

    parser.add_argument('--update', dest='update', action='store_true',
        default=False, help='(Re)index all paths')

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
    if api.ping():
        logger.debug('Connected to API at %s:%s' % (args.host, args.port))
    else:
        logger.debug('Failed to connect to API at %s:%s' % (args.host, args.port))
        return

    config = api.get_config()
    print(config)

    if args.list_paths:
        if not 'paths' in config:
            logger.error('No paths configured')
            return 1
        print('==> Indexed paths')
        for path in config['paths']:
            print('* %s' % path)
    elif args.add_path:
        if 'paths' in config:
            paths = config['paths']
        else:
            paths = []
        if args.add_path in paths:
            logger.error('Path already indexed')
            return 1
        paths.append(args.add_path)
        result = api.set_config('paths', paths)
        if not result:
            logger.error('Failed to set config.paths')
            return 1
    elif args.del_path:
        if 'paths' in config:
            if args.del_path in config['paths']:
                paths = []
                for path in config['paths']:
                    if path == args.del_path:
                        continue
                    paths.append(path)
                
                result = api.set_config('paths', paths)
                if not result:
                    logger.error('Failed to set config.paths')
                    return 1
            else:
                logger.error('Path no indexed')
        else:
            logger.error('No paths configured')
    elif args.update:
        mimetypes.init()
        indexers = []
        if not 'paths' in config:
            logger.error('No paths found')
            return 1
        for path in config['paths']:
            logger.debug('Starting thread for %s' % path)
            indexer = Indexer(logger, api, path)
            indexer.start()
            indexers.append(indexer)

        for indexer in indexers:
            indexer.join()

    return

if __name__ == '__main__':
    sys.exit(main())
