#!/usr/bin/env python

import argparse
import json
import logging
import requests
import sys
import time

import whoosh.fields

sys.path.append('/home/r3boot/fileindexer')

from fileindexer.backends.whoosh_index import WhooshIndex

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

def whoosh_write(wi, logger, buff, writers=4, limitmb=512):
    t_start = time.time()
    writer = wi.idx.writer(writers=writers, limitmb=limitmb)
    for doc in buff:
        try:
            writer.add_document(**doc)
        except whoosh.fields.UnknownFieldError, e:
            print(e)
            print(doc)
    writer.commit()
    logger.debug('Wrote %s documents in %.00f seconds' % (len(buff), time.time()-t_start))

def crawler_task(logger, url):
    metafile = '%s/00METADATA' % url

    _stringfields = ['url', 'full_path', 'filename', 'checksum', 'framerate', 'bitrate', 'samplerate', 'comment', 'endianness', 'compression', 'channel', 'language', 'title', 'author', 'artist', 'album', 'producer', 'video', 'audio', 'subtitle', 'file']

    session = requests.session()

    wi = WhooshIndex(logger)
    buff = []

    r = None
    try:
        r = session.get(metafile)
    except requests.exceptions.ConnectionError, e:
        print(e)
        return
    except ValueError, e:
        print(e)
        return
    finally:
        if r and r.status_code == 200:
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
                    buff.append(meta)
                except UnicodeDecodeError, e:
                    pass

                if len(buff) >= 1000:
                    whoosh_write(wi, logger, buff)
                    buff = []

            whoosh_write(wi, logger, buff)


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
