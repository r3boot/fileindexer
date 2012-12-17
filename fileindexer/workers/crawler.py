#!/usr/bin/env python

import json
import requests

def crawler(logger, session, url, out_q):

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

    idx = '%s/00INDEX' % url
    logger.debug('Parsing %s' % idx)

    response = __request(logger, session, url=idx, method='get')
    results = []
    if response['result']:
        for line in response['data'].split('\n'):
            if not '\t' in line:
                continue
            (filename, raw_meta) = line.split('\t')
            meta = json.loads(raw_meta)
            meta['filename'] = filename
            meta['url'] = '%s/%s' % (url, filename)
            results.append(meta)
    out_q.put(results)
