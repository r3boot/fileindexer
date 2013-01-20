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

def whoosh_write(wi, logger, buff, procs=4, limitmb=512):
    t_start = time.time()

    writer = wi.idx.writer(procs=procs, limitmb=limitmb, multisegment=True)

    ## Use an unbounded cache for the stemming analyzer
    """
    print(writer.schema["url"])
    for field in writer.schema.names():
        stem_analyzer = writer.schema[field].format.analyzer
        stem_analyzer = -1
        stem_analyzer.clear()
    """

    for doc in buff:
        #print(doc['url'])
        try:
            writer.add_document(**doc)
        except whoosh.fields.UnknownFieldError, e:
            print(e)
    writer.commit()
    logger.debug('Wrote %s documents in %.00f seconds' % (len(buff), time.time()-t_start))

def whoosh_commit(wi, procs=4, limitmb=512):
    writer = wi.idx.writer(procs=procs, limitmb=limitmb, multisegment=True)
    writer.commit()

def crawler_task(logger, url):
    metafile = '%s/00METADATA' % url

    _stringfields = ['url', 'full_path', 'filename', 'checksum', 'framerate', 'bitrate', 'samplerate', 'comment', 'endianness', 'compression', 'channel', 'language', 'title', 'author', 'artist', 'album', 'producer', 'video', 'audio', 'subtitle', 'file']

    session = requests.session()

    wi = WhooshIndex(logger)
    buff = []
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
    finally:
        if r and r.status_code == 200:
            t_start = time.time()
            with wi.idx.writer(procs=4, limitmb=512, multisegment=True) as writer:
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
                        writer.add_document(**meta)
                        total_docs += 1
                        #buff.append(meta)
                    except UnicodeDecodeError, e:
                        pass

                    """
                    if len(buff) >= 5000:
                        whoosh_write(wi, logger, buff)
                        buff = []
                    """

            logger.debug('Wrote %s documents in %.00f seconds' % (total_docs, time.time()-t_start))

            #whoosh_write(wi, logger, buff)

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
