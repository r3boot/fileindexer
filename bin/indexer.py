#!/usr/bin/env python

import argparse
import hashlib
import logging
import mimetypes
import multiprocessing
import os
import stat
import sys
#import tempfile
import time

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.log import get_logger
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.index_writer import IndexWriter
from fileindexer.backends.redis_queue import RedisQueue

__description__ = 'File Indexer'

_d_debug = False
_d_num_workers = 4
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
    queue = RedisQueue(logger, 'fileindexer')
    hmp = HachoirMetadataParser(logger)
    idxwriter = IndexWriter(logger)

    """
    fd_in = os.open(fifo_in, os.O_RDONLY)
    fd_out = os.open(fifo_out, os.O_WRONLY | os.O_NONBLOCK)
    """

    #empty_counter = 0
    #max_path_length = 2048
    while True:
        if queue.empty():
            print('Queue is empty')
            time.sleep(0.5)
            continue

        path = queue.get()
        """
        ch = None
        ch = os.read(fd_in, 1)
        if len(ch) == 0:
            if empty_counter == 5:
                logger.debug('(worker %s) Queue assumed empty, breaking' % worker_id)
                break
            else:
                logger.debug('(worker %s) Increasing empty_counter: %s' % (worker_id, empty_counter))
                empty_counter += 1
                time.sleep(1.0)

        path = None
        path = ''
        path_length = None
        path_length = 0
        while ch != '\n':
            if path_length > max_path_length:
                logger.warn('(worker %s) max_path_length reached, resetting' % worker_id)
                continue
            path += ch
            path_length += 1
            ch = os.read(fd_in, 1)

        if path == '!!__POISON__!!':
            logger.debug('(worker %s) Received poison pill, exiting' % worker_id)
            break
        """

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
                queue.put(full_path)
                ##os.write(fd_out, '%s\n' % full_path)

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

        idxwriter.write_indexes(path, results['metadata'])
    logger.debug('worker exiting')

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
    mp_pool = multiprocessing.Pool(processes=num_workers)
    queue = RedisQueue(logger, 'fileindexer')

    ## Preseed queue
    #input_buffer = []
    for path in args.path:
        queue.put(path)

    ## Fire up workers
    task_args = {
        'log_level': log_level,
        'do_stat': args.do_stat,
        'do_hachoir': args.do_hachoir,
        'quality': args.quality,
        'ignore_symlinks': args.ignore_symlinks,
        'excluded': excluded
    }
    mp_pool.map_async(indexer_task, [(worker_id, task_args) for worker_id in xrange(num_workers)])

    """
    tasks = []
    fifo_fds_in = []
    fifo_fds_out = []
    for worker in xrange(num_workers):
        (fd_in, fifo_in) = tempfile.mkstemp()
        (fd_out, fifo_out) = tempfile.mkstemp()
        fd_in = os.open(fifo_in, os.O_WRONLY | os.O_NONBLOCK)
        fd_out = os.open(fifo_out, os.O_RDONLY)
        tasks.append((fifo_in, fifo_out, args.do_stat, args.do_hachoir, args.quality, args.ignore_symlinks, excluded, log_level, worker))
        fifo_fds_in.append(fd_in)
        fifo_fds_out.append(fd_out)
    mp_pool.map_async(indexer_task, tasks)
    """

    while not queue.empty():
        logger.debug('queue size: %s' % queue.qsize())
        time.sleep(1)

    """
    quit_loop = False
    max_path_size = 2048
    j = 0
    while not quit_loop:
        ## Fill input_buffer
        reset_path = None
        reset_path = False
        ch = None
        for i in xrange(num_workers):
            path = None
            path = ''
            path_size = None
            path_size = 0
            ch = os.read(fifo_fds_out[i], 1)
            while ch != '':
                if path_size > max_path_size:
                    logger.warn('max_path_size reached, resetting')
                    reset_path = True
                    break
                if ch == '\n':
                    if reset_path:
                        path = None
                        path = ''
                        reset_path = False
                    break
                path += ch
                path_size += 1
                ch = os.read(fifo_fds_out[i], 1)

            if len(path) > 0:
                input_buffer.append(path)
        i = None

        ## Flush input_buffer
        for item in input_buffer:
            if j == num_workers:
                j = None
                j = 0
            os.write(fifo_fds_in[j], '%s\n' % item)
            j += 1
        item = None
        input_buffer = None
        input_buffer = []
    """

    mp_pool.close()
    mp_pool.join()

if __name__ == "__main__":
    main()
