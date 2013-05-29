#!/usr/bin/env python

import Queue
import argparse
import datetime
import hashlib
import json
import logging
import multiprocessing
import os
import stat
import sys
import time

import pprint

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.constants import category_types

from fileindexer.indexer import MetadataParser
from fileindexer.indexer.parser_utils import *
from fileindexer.indexer.meta_postproc import MetadataPostProcessor

__description__ = 'File Indexer'

_d_debug = False
_d_num_workers = 4
_d_resume = False
_d_do_stat = True
_d_do_metadata = True
_d_hachoir_quality = 0.5
_d_ignore_symlinks = True

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

def indexer_worker(worker_id, work_q, result_q, log_level):

    mp = MetadataParser()
    mpp = MetadataPostProcessor()

    info("Spawning worker %s" % worker_id)

    while True:
        path = None
        path = work_q.get()
        result_q.put(worker_id+100)

        if path == '!DIE!':
            warning('(worker %s) Received kill-pill, exiting' % worker_id)
            break

        info('(worker %s) Indexing: %s' % (worker_id, path))

        results = None
        results = []
        if not os.access(path, os.R_OK | os.X_OK):
            error('(worker %s) Cannot access %s' % (worker_id, path))
            continue

        found = None
        for found in os.listdir(path):
            ## Send keepalive
            result_q.put(worker_id+100)

            # TODO
            #if found in kwargs['excluded']:
            #    continue

            found = safe_unicode(found)
            if not found:
                continue

            path = safe_unicode(path)
            if not path:
                continue

            meta = None
            meta = {
                'category': None,
                'file': {},
                'url': None,
            }
            meta['file']['name'] = found

            full_path = None
            full_path = safe_unicode(os.path.join(path, found))
            if not full_path:
                continue

            meta['file']['path'] = full_path
            # info('working on %s' % full_path)

            st = None
            try:
                st = os.stat(full_path)
            except OSError, errmsg:
                error('(worker %s) Cannot stat %s: %s' % (worker_id, full_path, errmsg))
                continue

            if stat.S_ISLNK(st.st_mode):
                warning('(worker %s) Skipping symlink %s' % (worker_id, full_path))
                continue

            if stat.S_ISDIR(st.st_mode):
                meta['category'] = category_types['dir']
                work_q.put(full_path)
                continue

            meta['file']['checksum'] = hashlib.md5(
                '%s %s' % (st.st_ctime, st.st_size)
            ).hexdigest()

            meta['file']['mode'] = st.st_mode
            meta['file']['uid'] = st.st_uid
            meta['file']['gid'] = st.st_gid
            meta['file']['size'] = st.st_size
            meta['file']['atime'] = st.st_atime
            meta['file']['mtime'] = st.st_mtime
            meta['file']['ctime'] = st.st_ctime

            meta = mp.extract(meta, full_path)
            meta = mpp.process(meta)

            results.append(meta)
            #pprint.pprint(results)

        if len(results) > 0:
            result_q.put(results)

    print('worker exiting')

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('path', metavar='PATH', type=str,
        nargs='+', help='Path to index')

    parser.add_argument('--workers', dest='num_workers', action='store',
        default=_d_num_workers, help='Number of indexer workers')

    parser.add_argument('--disable-stat', dest='do_stat', action='store_false',
        default=_d_do_stat, help='Disable indexing of stat() information')
    parser.add_argument('--disable-metadata', dest='do_metadata', action='store_false',
        default=_d_do_metadata, help='Disable extraction and indexing of metadata')
    parser.add_argument('--enable-symlinks', dest='ignore_symlinks', action='store_true',
        default=_d_ignore_symlinks, help='Follow symlinks')

    args = parser.parse_args()

    logger = logging.getLogger('main')
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    console_logger = logging.StreamHandler()
    console_logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)

    print('logging at %s' % ll2str[log_level])
    print('num_workers: %s' % args.num_workers)

    ## Setup multiprocessing
    num_workers = int(args.num_workers)
    work_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()

    print('Spawning workers')
    procs = {}
    for i in xrange(num_workers):
        p = multiprocessing.Process(
            target=indexer_worker,
            args=(i, work_q, result_q, log_level)
        )
        procs[i] = p
        p.start()

    print('Seeding work queue')
    work_q.put(args.path[0])
    time.sleep(1.0)

    print('Gathering and sorting metadata')
    all_meta = []
    empty_count = 0
    max_empty_count = 25

    while True:
        if empty_count > max_empty_count:
            print('Queue is empty')
            break

        result = None
        try:
            result = result_q.get_nowait()
            empty_count = 0
        except Queue.Empty:
            if work_q.qsize() > 0:
                print('Waiting for results (work:%s)' % work_q.qsize())
                time.sleep(1.0)
            else:
                empty_count += 1
                time.sleep(0.1)
            continue

        if result:
            if isinstance(result, int):
                ## Received keepalive
                pass
            else:
                [all_meta.append(m) for m in result]
        else:
            time.sleep(0.1)

    all_paths = {}
    for meta in all_meta:
        all_paths[meta['file']['path']] = meta
    all_paths_idx = all_paths.keys()
    all_paths_idx.sort()

    for i in xrange(num_workers):
        work_q.put('!DIE!')
    time.sleep(0.2)

    print('Cleaning up leftover workers')
    for k in procs.keys():
        p = procs[k]
        if p.is_alive():
            print('Terminating worker %s' % k)
            p.terminate()
            p.join()

    print('Writing metadata')
    fd = open('%s/00METADATA' % args.path[0], "w")
    fd.write('# fileindexer v=0.1\n')
    prefix_length = len(args.path[0])+1
    for path in all_paths_idx:
        path = safe_unicode(path)
        if not path:
            continue
        meta = all_paths[path]
        path = path[prefix_length:]

        try:
            meta = json.dumps(meta)
        except TypeError, e:
            print(e)
            print(meta)
            continue
        except UnicodeDecodeError, e:
            print(e)
            print(meta)
            continue
        fd.write(path.encode('UTF-8'))
        fd.write('\t')
        fd.write(meta)
        fd.write('\n')
    os.fsync(fd)
    fd.close()

if __name__ == "__main__":
    main()
