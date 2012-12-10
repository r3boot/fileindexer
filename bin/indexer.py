#!/usr/bin/env python

import argparse
import logging
import mimetypes
import sys

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.api.client import APIClient as API
from fileindexer.indexer import Indexer

__description__ = 'Add description'

_d_debug = False
_d_host = '127.0.0.1'
_d_port = '5423'
_d_quality = 0.5

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('-H', dest='host', action='store',
        default=_d_host, help='Host to connect to, defaults to %s' % _d_host)
    parser.add_argument('-P', dest='port', action='store',
        default=_d_port, help='Port to connect to, defaults to %s' % _d_port)

    parser.add_argument('--apikey', dest='apikey', action='store',
        default=False, help='Key for API')

    parser.add_argument('--add', dest='add_index', action='store',
        default=False, help='Add path to index')
    parser.add_argument('--name', dest='add_index_name', action='store',
        default=False, help='Name for new index')
    parser.add_argument('--description', dest='add_index_descr', action='store',
        default=False, help='Description for new index')
    parser.add_argument('--del', dest='del_index', action='store',
        default=False, help='Remove path from index')
    parser.add_argument('--list', dest='list_indexes', action='store_true',
        default=False, help='Display all indexed paths')

    parser.add_argument('--update', dest='update', action='store_true',
        default=False, help='(Re)index all paths')

    parser.add_argument('--no-stat', dest='no_stat', action='store_true',
        default=False, help='Do not store stat() information')
    parser.add_argument('--no-meta', dest='no_meta', action='store_true',
        default=False, help='Do not store file metadata')
    parser.add_argument('--quality', dest='quality', action='store', type=float,
        default=_d_quality, help='Quality of metadata scan (0.0(low) .. 1.0(high))')
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

    if not args.apikey:
        logger.error('You need to specify an api key')
        return 1

    api = API(logger, args.host, args.port, args.apikey)
    if api.ping():
        logger.debug('Connected to API at %s:%s' % (args.host, args.port))
    else:
        logger.error('Failed to connect to API at %s:%s' % (args.host, args.port))
        return

    if args.list_indexes:
        response = api.get_indexes()
        if not response['result']:
            logger.error('Failed to retrieve indexes: %s' % response['message'])
            return 1
        print('==> Indexed paths')
        for idx in response['indexes']:
            print('* %s' % idx['path'])
    elif args.add_index:
        response = api.get_indexes()
        if response['result']:
            for idx in response['indexes']:
                if args.add_index == idx['path']:
                    logger.error('Path already indexed')
                    return 1

        result = api.add_index(args.add_index, args.add_index_name, args.add_index_descr)
        if not result:
            logger.error('Failed to add index')
            return 1
    elif args.del_index:
        response = api.get_indexes()
        if not response['result']:
            logger.error('Failed to retrieve indexes: %s' % response['message'])
            return 1

        result = api.remove_index(args.del_index)
        if not result:
            logger.error('Failed to remove index')
            return 1
    elif args.update:
        mimetypes.init()
        indexers = []
        response = api.get_indexes()
        if not response['result']:
            logger.error('Failed to retrieve indexes: %s' % response['message'])
            return 1
        for idx in response['indexes']:
            logger.debug('Starting thread for %s' % idx['path'])
            indexer = Indexer(logger, api, idx)
            indexer.start()
            indexers.append(indexer)

        for indexer in indexers:
            indexer.join()

    return

if __name__ == '__main__':
    sys.exit(main())
