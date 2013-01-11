#!/usr/bin/env python

import argparse
import json
import logging
import multiprocessing
import requests
import sys
import time

sys.path.append('/home/r3boot/fileindexer')

from fileindexer.log import get_logger
from fileindexer.backends.filesystem_queue import FilesystemQueue

__description__ = 'Add description'

_d_debug = False
_d_num_workers = 4

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

session = requests.session()

def __request(logger, session, url, method):
    response = {}
    r = None
    try:
        r = session.get(url)
    except requests.exceptions.ConnectionError, e:
        r = False
        response['result'] = False
        response['message'] = e
        logger.error(e)
    except ValueError, e:
        r = False
        response['result'] = False
        response['message'] = e
        logger.error(e)
    finally:
        if r and r.status_code == 200:
            response['result'] = True
            response['data'] = r.content
        else:
            response['result'] = False
            response['message'] = 'Request failed'
    return response

def crawler_task(args):
    worker_id = args[0]
    kwargs = args[1]

    logger = get_logger(kwargs['log_level'])
    in_q = FilesystemQueue('out_q')
    out_q = FilesystemQueue('out_q')

    empty_counter = 0
    stop = False
    while not stop:
        if empty_counter > kwargs['max_empty_time']:
            logger.debug('worker %s) Queue is empty, exiting' % worker_id)
            break

        if in_q.empty():
            empty_counter += 1
            time.sleep(1)
            continue
        else:
            empty_counter = 0

        url = None
        url = in_q.get()
        idx = None
        idx = '%s/00INDEX' % url

        response = __request(logger, session, url=idx, method='get')
        results = []
        if response['result']:
            for line in response['data'].split('\n'):
                if not '\t' in line:
                    continue
                (filename, raw_meta) = line.split('\t')
                meta = json.loads(raw_meta)
                meta['filename'] = filename
                meta['url'] = '%s/%s' % (kwargs['url'], filename)
                results.append(meta)

        if len(results) > 0:
            out_q.put(results)

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('url', metavar='URL', type=str,
        nargs='+', help='URL to crawl')

    parser.add_argument('--workers', dest='num_workers', action='store',
        default=_d_num_workers, help='Number of crawler workers')

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

    num_workers = int(args.num_workers)
    mp_pool = multiprocessing.Pool(processes=num_workers)
    in_q = FilesystemQueue('in_q')
    out_q = FilesystemQueue('out_q')
    max_empty_time = 30

    task_args = {
        'log_level': log_level,
        'max_empty_time': max_empty_time
    }
    mp_pool.map_async(crawler_task, [(worker_id, task_args) for worker_id in xrange(num_workers)])

    in_empty_count = 0
    out_empty_count = 0
    while True:
        if in_empty_count > max_empty_time and out_empty_count > max_empty_time:
            logger.debug('Queue empty, exiting')
            break

        if in_q.empty():
            in_empty_count += 1
        else:
            in_empty_count = 0

        if out_q.empty():
            out_empty_count += 1
        else:
            out_empty_count = 0

        results = out_q.get()

        for meta in results:
            if meta['is_dir']:
                in_q.put(meta['url'])

if __name__ == '__main__':
    sys.exit(main())
