#!/usr/bin/env python

import Queue
import argparse
import hashlib
import json
import logging
import mimetypes
import multiprocessing
import os
import stat
import sys
import time

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.log import get_logger
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper

__description__ = 'File Indexer'

_d_debug = False
_d_num_workers = 4
_d_resume = False
_d_do_stat = True
_d_do_hachoir = True
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

    logger = get_logger(log_level)
    hmp = HachoirMetadataParser(logger)

    logger.debug("Spawning worker %s" % worker_id)

    while True:
        path = None
        path = work_q.get()
        result_q.put(worker_id+100)

        if path == '!DIE!':
            print('worker %s) Received kill-pill, exiting' % worker_id)
            break

        print('(worker %s) Indexing: %s' % (worker_id, path))

        results = None
        results = {}
        results['path'] = path
        results['metadata'] = []
        if not os.access(path, os.R_OK | os.X_OK):
            logger.warn('(worker %s) Cannot access %s' % (worker_id, path))
            continue

        found = None
        for found in os.listdir(path):
            result_q.put(worker_id+100)

            # TODO
            #if found in kwargs['excluded']:
            #    continue
            try:
                found = unicode(found)
            except UnicodeDecodeError:
                logger.warn('(worker %s) Cannot encode %s to unicode' % (worker_id, found))
                continue

            try:
                path = unicode(path)
            except UnicodeDecodeError:
                logger.warn('(worker %s) Cannot encode %s to unicode' % (worker_id, found))
                continue

            meta = None
            meta = {}
            meta['filename'] = found

            full_path = None
            full_path = os.path.join(path, found)
            meta['full_path'] = full_path

            if os.path.islink(full_path):
                logger.warn('(worker %s) Skipping symlink %s' % (worker_id, full_path))
                continue

            st = None
            try:
                st = os.stat(full_path)
            except OSError, e:
                logger.warn('(worker %s) Cannot stat %s' % (worker_id, full_path))
                logger.warn(e)
                continue

            meta['is_dir'] = stat.S_ISDIR(st.st_mode)
            if meta['is_dir']:
                work_q.put(full_path)

            meta['checksum'] = hashlib.md5('%s %s' % (st.st_ctime, st.st_size)).hexdigest()

            meta['mode'] = st.st_mode
            meta['uid'] = st.st_uid
            meta['gid'] = st.st_gid
            meta['size'] = st.st_size
            meta['atime'] = st.st_atime
            meta['mtime'] = st.st_mtime
            meta['ctime'] = st.st_ctime

            if not meta['is_dir']:
                types = None
                types = mimetypes.guess_type(full_path)
                if types[0] != None:
                    meta['mime'] = types[0]
                if types and types[0] != None:
                    t = None
                    for mimetype in types:
                        if mimetype in hachoir_mapper:
                            t = mimetype
                            break
                    if t:
                        hmp_meta = None
                        hmp_meta = hmp.extract(full_path, 0.5,  hachoir_mapper[t])
                        if hmp_meta:
                            k = None
                            v = None
                            for k,v in hmp_meta.items():
                                meta[k] = v

            results['metadata'].append(meta)

        result_q.put(results['metadata'])

    logger.debug('worker exiting')

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('path', metavar='PATH', type=str,
        nargs='+', help='Path to index')

    parser.add_argument('--workers', dest='num_workers', action='store',
        default=_d_num_workers, help='Number of indexer workers')
    parser.add_argument('--resume', dest='resume', action='store_true',
        default=_d_resume, help='Continue a previously broken off index run')

    parser.add_argument('--disable-stat', dest='do_stat', action='store_false',
        default=_d_do_stat, help='Disable indexing of stat() information')
    parser.add_argument('--disable-metadata', dest='do_hachoir', action='store_false',
        default=_d_do_hachoir, help='Disable extraction and indexing of metadata')
    parser.add_argument('--enable-symlinks', dest='ignore_symlinks', action='store_true',
        default=_d_ignore_symlinks, help='Follow symlinks')
    parser.add_argument('--quality', dest='quality', action='store',
        type=float, default=_d_hachoir_quality, help='Amount of effort used to extract metadata (0.1..1.0)')

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger = get_logger(log_level)
    logger.debug('logging at %s' % ll2str[log_level])
    logger.debug('num_workers: %s' % args.num_workers)

    ## Setup multiprocessing
    num_workers = int(args.num_workers)
    work_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()

    logger.debug('Spawning workers')
    procs = {}
    for i in xrange(num_workers):
        p = multiprocessing.Process(
            target=indexer_worker,
            args=(i, work_q, result_q, log_level)
        )
        procs[i] = p
        p.start()

    logger.debug('Seeding work queue')
    work_q.put(args.path[0])
    time.sleep(1.0)

    logger.debug('Gathering and sorting metadata')
    all_meta = []
    empty_count = 0
    max_empty_count = 500
    worker_idle_count = {}
    max_worker_idle_count = 250
    for i in xrange(num_workers):
        worker_idle_count[i] = 0

    while True:
        if empty_count > max_empty_count:
            logger.debug('Queue is empty')
            break

        """
        ## TODO: this needs a proper look at and fixing the
        ##       reason *why* processes are hanging
        for i in xrange(num_workers):
            worker_idle_count[i] += 1
            if worker_idle_count[i] > max_worker_idle_count:
                logger.debug('Worker %s is hanging, restarting' % i)
                procs[i].terminate()
                procs[i] = None
                p = multiprocessing.Process(
                    target=indexer_worker,
                    args=(i, work_q, result_q, log_level)
                )
                procs[i] = p
                p.start()
                worker_idle_count[i] = 0
        """

        result = None
        try:
            result = result_q.get_nowait()
            empty_count = 0
        except Queue.Empty:
            print('Queue is empty (work:%s; results:%s; empty:%s)' % (work_q.qsize(), result_q.qsize(), empty_count))
            empty_count += 1
            time.sleep(0.1)
            continue

        if result:
            if isinstance(result, int):
                worker_idle_count[result-100] = 0
            else:
                [all_meta.append(m) for m in result]
        else:
            time.sleep(0.1)

    all_meta.sort()

    for i in xrange(num_workers):
        work_q.put('!DIE!')
    time.sleep(0.2)

    logger.debug('Cleaning up leftover workers')
    for k in procs.keys():
        p = procs[k]
        if p.is_alive():
            logger.debug('Terminating worker %s' % k)
            p.terminate()
            p.join()

    logger.debug('Writing metadata')
    fd = open('%s/00METADATA' % args.path[0], "w")
    fd.write('# fileindexer-0.1\n')
    for meta in all_meta:
        path = meta['full_path'].replace('%s/' % args.path[0], '').encode('utf-8')
        meta = json.dumps(meta).encode('utf-8')
        fd.write('%s\t%s\n' % (path, meta))
    os.fsync(fd)
    fd.close()

if __name__ == "__main__":
    main()
