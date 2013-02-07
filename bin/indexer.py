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
from fileindexer.indexer.safe_unicode import safe_unicode
from fileindexer.indexer.file_meta_parser import FileMetadataParser
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.enzyme_meta_parser import EnzymeMetadataParser, enzyme_mimes
from fileindexer.indexer.mutagen_meta_parser import MutagenMetadataParser, mutagen_mimes
from fileindexer.indexer.exif_meta_parser import ExifMetadataParser, exif_mimes
from fileindexer.indexer.meta_postproc import MetadataPostProcessor

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
    fmp = FileMetadataParser()
    hmp = HachoirMetadataParser(logger)
    emp = EnzymeMetadataParser()
    mmp = MutagenMetadataParser()
    Emp = ExifMetadataParser()
    mpp = MetadataPostProcessor()

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
        results = []
        if not os.access(path, os.R_OK | os.X_OK):
            logger.warn('(worker %s) Cannot access %s' % (worker_id, path))
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
                scan_with_file = True
                scan_with_hachoir = False
                scan_with_mutagen = False
                scan_with_exif = False

                types = None
                types = mimetypes.guess_type(full_path)

                if types and types[0] != None:
                    meta['mime'] = types[0]
                    #if not scan_with_hachoir and meta['mime'] in hachoir_mapper:
                    if not scan_with_hachoir and meta['mime'] in enzyme_mimes:
                        scan_with_hachoir = True
                    if not scan_with_mutagen and meta['mime'] in mutagen_mimes:
                        scan_with_mutagen = True
                    if not scan_with_exif and meta['mime'] in exif_mimes:
                        scan_with_exif = True

                if scan_with_file:
                    fmp_meta = None
                    fmp_meta = fmp.extract(meta)
                    if fmp_meta:
                        #print("fmp_meta: %s" % fmp_meta)
                        meta.update(fmp_meta)

                if scan_with_hachoir:
                    emp_meta = None
                    emp_meta = emp.extract(meta)
                    if emp_meta:
                        #print('emp_meta: %s' % emp_meta)
                        meta.update(emp_meta)
                    else:
                        hmp_meta = None
                        hmp_meta = hmp.extract(meta, 0.5,  hachoir_mapper[meta['mime']])
                        if hmp_meta:
                            #print('hmp_meta: %s' % hmp_meta)
                            meta.update(hmp_meta)

                if scan_with_mutagen:
                    #print('[*] Scanning %s with mutagen' % meta['filename'])
                    mmp_meta = None
                    mmp_meta = mmp.extract(meta)
                    if mmp_meta:
                        #print('mmp_meta: %s' % mmp_meta)
                        meta.update(mmp_meta)
                    
                if scan_with_exif:
                    #print('[*] Scanning %s with EXIF' % meta['filename'])
                    Emp_meta = None
                    Emp_meta = Emp.extract(meta)
                    if Emp_meta:
                        #print('Emp_meta: %s' % Emp_meta)
                        meta.update(Emp_meta)

            for k,v in mpp.process(meta).items():
                meta[k] = v
            results.append(meta)

        if len(results) > 0:
            result_q.put(results)

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
    max_empty_count = 25

    while True:
        if empty_count > max_empty_count:
            logger.debug('Queue is empty')
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
        all_paths[meta['full_path']] = meta
    all_paths_idx = all_paths.keys()
    all_paths_idx.sort()

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
