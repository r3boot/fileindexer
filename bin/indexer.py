#!/usr/bin/env python

import argparse
import hashlib
import logging
import mimetypes
import multiprocessing
import os
import stat
import sys
import tempfile
import time

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.log import get_logger
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.index_writer import IndexWriter

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
    fifo_in = args[0]
    fifo_out = args[0]
    out_q = args[1]
    do_stat = args[2]
    do_hachoir = args[3]
    hachoir_quality = args[4]
    ignore_symlinks = args[5]
    excluded = args[6]
    log_level = args[7]
    lock = args[8]

    logger = get_logger(log_level)
    hmp = HachoirMetadataParser(logger)
    idxwriter = IndexWriter(logger)

    fd_in = os.open(fifo_in, os.O_RDONLY)
    fd_out = os.open(fifo_out, os.O_WRONLY | os.O_NONBLOCK)

    empty_counter = 0
    while True:
        ch = os.read(fd_in, 1)
        if ch == '':
            if empty_counter == 60:
                break
            else:
                empty_counter += 1
                time.sleep(1.0)
        path = ''
        while ch != '\n':
            path += ch
            ch = os.read(fd_in, 1)
        print('path: %s' % path)

        if path == '!!__POISON__!!':
            logger.debug('Received poison pill, exiting')
            break

        #logger.debug('get: %s' % path)

        results = {}
        results['path'] = path
        results['metadata'] = []
        if not os.access(path, os.R_OK | os.X_OK):
            logger.warn('Cannot access %s' % path)
            continue

        for found in os.listdir(path):
            if found in excluded:
                continue
            try:
                found = unicode(found)
            except UnicodeDecodeError:
                logger.warn('Cannot encode %s to unicode' % found)
                continue

            try:
                path = unicode(path)
            except UnicodeDecodeError:
                logger.warn('Cannot encode %s to unicode' % found)
                continue

            meta = {}
            meta['filename'] = found

            full_path = os.path.join(path, found)
            try:
                st = os.stat(full_path)
            except OSError, e:
                logger.warn('Cannot stat %s' % full_path)
                logger.warn(e)
                continue

            if ignore_symlinks and stat.S_ISLNK(st.st_mode):
                logger.warn('Skipping symlink %s' % full_path)
                continue

            meta['is_dir'] = stat.S_ISDIR(st.st_mode)
            if meta['is_dir']:
                os.write(fd_out, '%s\n' % full_path)

            meta['checksum'] = hashlib.md5('%s %s' % (found, st.st_size)).hexdigest()

            if do_stat:
                meta['mode'] = st.st_mode
                meta['uid'] = st.st_uid
                meta['gid'] = st.st_gid
                meta['size'] = st.st_size
                meta['atime'] = st.st_atime
                meta['mtime'] = st.st_mtime
                meta['ctime'] = st.st_ctime

            if not meta['is_dir'] and do_hachoir:
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
                        hmp_meta = hmp.extract(full_path, hachoir_quality,  hachoir_mapper[t])
                        if hmp_meta:
                            for k,v in hmp_meta.items():
                                meta[k] = v

            results['metadata'].append(meta)

        idxwriter.write_indexes(path, results['metadata'])
    else:
        logger.debug('Waiting for work')
        time.sleep(1.0)
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
    manager = multiprocessing.Manager()
    in_q = manager.Queue()
    out_q = manager.Queue()
    lock = manager.Lock()
    pool = multiprocessing.Pool(processes=num_workers)

    ## Preseed queue
    input_buffer = []
    for path in args.path:
        input_buffer.append(path)

    ## Fire up workers
    tasks = []
    fifo_fds_in = []
    fifo_fds_out = []
    for worker in xrange(num_workers):
        (fd_in, fifo_in) = tempfile.mkstemp()
        (fd_out, fifo_out) = tempfile.mkstemp()
        fd_in = os.open(fifo_in, os.O_WRONLY | os.O_NONBLOCK)
        fd_out = os.open(fifo_out, os.O_RDONLY)
        tasks.append((fifo_in, fifo_out, args.do_stat, args.do_hachoir, args.quality, args.ignore_symlinks, excluded, log_level, lock))
        fifo_fds_in.append(fd_in)
        fifo_fds_out.append(fd_out)
    print(tasks)
    pool.map_async(indexer_task, tasks)

    i = 0
    while True:
        for item in input_buffer:
            if i == num_workers:
                i = 0
            logger.debug('sending job to worker %s' % i)
            os.write(fifo_fds_in[i], '%s\n' % item)
            i += 1
        input_buffer = []
        for i in xrange(num_workers):
            ch = os.read(fifo_fds_out[i], 1)
            if ch == '':
                break
            path = ''
            while ch != '\n':
                path += ch
                ch = os.read(fifo_fds_out[i], 1)
            input_buffer.append(path)

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
