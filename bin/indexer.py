#!/usr/bin/env python

import argparse
import logging
#import mimetypes
import sys

sys.path.append('/people/r3boot/fileindexer')

#from fileindexer.api.client import APIClient as API
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

    parser.add_argument('path', metavar='PATH', type=str,
        nargs='+', help='Path to index')

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

    indexers = []
    for path in args.path:
        indexer = Indexer(logger, path)
        indexer.start()
        indexers.append(indexer)

    for indexer in indexers:
        indexer.join()

    return

if __name__ == '__main__':
    sys.exit(main())
