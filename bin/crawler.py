#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import requests
import sys
import time

sys.path.append('/home/r3boot/fileindexer')

from fileindexer.backends.elasticsearch_index import ElasticSearchIndex

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

def crawler_task(logger, url):
    metafile = '%s/00METADATA' % url

    _stringfields = ['url', 'filename', 'checksum', 'framerate', 'bitrate', 'samplerate', 'comment', 'endianness', 'compression', 'channel', 'language', 'title', 'author', 'artist', 'album', 'producer', 'video', 'audio', 'subtitle', 'file']
    _datefields = ['atime', 'ctime', 'mtime']
    _floatfields = ['size', 'uid', 'gid', 'mode', 'audio_bitrate', 'channels', 'compression_rate', 'duration', 'framerate', 'width', 'height', 'samplerate', 'video_bitrate']

    session = requests.session()

    esi = ElasticSearchIndex()

    total_docs = 0

    r = None
    try:
        r = session.get(metafile)
    except requests.exceptions.ConnectionError, e:
        print(e)
        return
    except ValueError, e:
        print(e)
        return

    if r and r.status_code == 200:
        t_start = time.time()
        for raw_meta in r.content.split('\n'):
            if not '\t' in raw_meta:
                continue
            (filename, raw_meta) = raw_meta.split('\t')
            meta = json.loads(raw_meta)
            meta['filename'] = filename
            try:
                meta['url'] = u'%s/%s' % (url, filename)
                for field in _stringfields:
                    if meta.has_key(field):
                        meta[field] = unicode(meta[field])
                for field in _datefields:
                    meta[field] = datetime.datetime.fromtimestamp(meta[field])
                for field in _floatfields:
                    if not field in meta.keys():
                        continue
                    if not isinstance(meta[field], float):
                        #print("field: %s" % meta[field])
                        meta[field] = float(meta[field])
                if 'full_path' in meta:
                    del(meta['full_path'])
                esi.index(meta)
                total_docs += 1
            except UnicodeDecodeError, e:
                    pass

    logger.debug('Wrote %s documents in %.00f seconds' % (total_docs, time.time()-t_start))

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

    crawler_task(logger, args.url[0])

if __name__ == '__main__':
    sys.exit(main())
