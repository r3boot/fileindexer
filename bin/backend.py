#!/usr/bin/env python

import argparse
import logging
import multiprocessing
import sys
import time

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.workers.backendapi import backend_api

__description__ = 'File Indexer Backend Daemon'

_d_debug = False
_d_listen_ip = '127.0.0.1'
_d_listen_port = '5423'

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

    parser.add_argument('-L', dest='listen_ip', action='store',
        default=_d_listen_ip, help='Where to listen on, defaults to %s' % (_d_listen_ip))
    parser.add_argument('-P', dest='listen_port', action='store',
        default=_d_listen_port, help='Port to listen on, defaults to %s' % (_d_listen_port))

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

    processes = []
    p_writeq_in = multiprocessing.Queue()

    ## Backend API
    beapi_proc = multiprocessing.Process(
        target=backend_api,
        args=(logger, args.listen_ip, args.listen_port, p_writeq_in)
    )
    beapi_proc.daemon = True
    beapi_proc.start()
    processes.append(beapi_proc)

    for proc in processes:
        proc.join()

    return

if __name__ == '__main__':
    sys.exit(main())
