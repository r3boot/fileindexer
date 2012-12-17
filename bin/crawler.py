#!/usr/bin/env python

from gevent import monkey; monkey.patch_all()

import argparse
import logging
import sys

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.workers.crawlerfeeder import CrawlerFeeder

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

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('url', metavar='URL', type=str,
        nargs='+', help='URL to crawl')

    parser.add_argument('--backend', dest='backend', action='store',
        default=_d_backend, help='URL for backend')

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

    crawler_feeder = CrawlerFeeder(logger, args.url)
    crawler_feeder.run()

if __name__ == '__main__':
    sys.exit(main())
