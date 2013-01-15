#!/usr/bin/env python

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
from fileindexer.backends.filesystem_queue import FilesystemQueue

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

def indexer_task(args):
    worker_id = args[0]
    kwargs = args[1]

    logger = get_logger(kwargs['log_level'])
    in_q = FilesystemQueue('indexer_in_q', '/tmp')
    out_q = FilesystemQueue('indexer_out_q', '/tmp')
    hmp = HachoirMetadataParser(logger)

    empty_counter = 0
    while empty_counter < kwargs['max_empty_time']:

        """
        print("Checking if queue has items")
        if in_q.empty():
            empty_counter += 1
            time.sleep(0.5)
            print("in_q is empty")
            continue
        else:
            empty_counter = 0
        """

        print("Retrieving path from queue")
        path = None
        path = in_q.get()
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
            if found in kwargs['excluded']:
                continue
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
            st = None
            try:
                st = os.stat(full_path)
            except OSError, e:
                logger.warn('(worker %s) Cannot stat %s' % (worker_id, full_path))
                logger.warn(e)
                continue

            if kwargs['ignore_symlinks'] and stat.S_ISLNK(st.st_mode):
                logger.warn('(worker %s) Skipping symlink %s' % (worker_id, full_path))
                continue

            meta['is_dir'] = stat.S_ISDIR(st.st_mode)
            if meta['is_dir']:
                in_q.put(full_path)

            meta['checksum'] = hashlib.md5('%s %s' % (found, st.st_size)).hexdigest()

            if kwargs['do_stat']:
                meta['mode'] = st.st_mode
                meta['uid'] = st.st_uid
                meta['gid'] = st.st_gid
                meta['size'] = st.st_size
                meta['atime'] = st.st_atime
                meta['mtime'] = st.st_mtime
                meta['ctime'] = st.st_ctime

            if not meta['is_dir'] and kwargs['do_hachoir']:
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
                        hmp_meta = hmp.extract(full_path, kwargs['quality'],  hachoir_mapper[t])
                        if hmp_meta:
                            for k,v in hmp_meta.items():
                                meta[k] = v

            results['metadata'].append(meta)

        #idxwriter.write_indexes(path, results['metadata'])
        out_q.put(results['metadata'])

    logger.debug('worker %s) Queue is empty, exiting' % empty_counter)
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

    excluded = ['00INDEX']

    ## Setup multiprocessing
    num_workers = int(args.num_workers)
    mp_pool = multiprocessing.Pool(processes=num_workers, maxtasksperchild=100)
    in_q = FilesystemQueue('indexer_in_q', '/tmp')
    out_q = FilesystemQueue('indexer_out_q', '/tmp')
    max_empty_time = 10

    if not args.resume:
        in_q.clear()
        in_q.put(args.path[0])

    ## Fire up workers
    task_args = {
        'log_level': log_level,
        'do_stat': args.do_stat,
        'do_hachoir': args.do_hachoir,
        'quality': args.quality,
        'ignore_symlinks': args.ignore_symlinks,
        'excluded': excluded,
        'max_empty_time': max_empty_time
    }
    mp_pool.map_async(indexer_task, [(worker_id, task_args) for worker_id in xrange(num_workers)])

    empty_count = 0
    while empty_count < max_empty_time:
        if in_q.empty():
            empty_count += 1
            time.sleep(0.5)
        else:
            empty_count = 0
        logger.debug('Waiting for queue')

    logger.debug("Queue is empty")
    mp_pool.close()
    mp_pool.join()

    logger.debug('Writing 00METADATA')
    all_meta = []
    while not out_q.empty():
        metas = None
        metas = out_q.get()
        [all_meta.append(meta) for meta in metas]

    all_meta.sort()
    fd = open('%s/00METADATA' % args.path[0], "w")
    for meta in all_meta:
        fd.write('%s||%s' % (meta['full_path'].replace(args.path, ''), json.dumps(meta)))
    os.fsync(fd)
    fd.close()

if __name__ == "__main__":
    main()
