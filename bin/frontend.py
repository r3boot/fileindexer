#!/usr/bin/env python

import argparse
import bottle
import logging
import sys

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.api.server import APIServer as API

__description__ = 'File Indexer Daemon'

_d_debug = False
_d_listen_ip = '127.0.0.1'
_d_listen_port = '5423'

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('-L', dest='listen_ip', action='store',
        default=_d_listen_ip, help='Where to listen on, defaults to %s' % (_d_listen_ip))
    parser.add_argument('-P', dest='listen_port', action='store',
        default=_d_listen_port, help='Port to listen on, defaults to %s' % (_d_listen_port))

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

    api = API(logger, args.listen_ip, args.listen_port)

    ## Webapp
    bottle.route('/',                method='GET')    (api.webapp)
    bottle.route('/js/:filename',    method='GET')    (api.serve_js)
    bottle.route('/css/:filename',   method='GET')    (api.serve_css)
    bottle.route('/img/:filename',   method='GET')    (api.serve_png)

    ## API
    bottle.route('/ping',    method='GET')    (api.ping)
    bottle.route('/auth',    method='GET')    (api.test_authentication)
    bottle.route('/users',   method='GET')    (api.get_users)
    bottle.route('/users',   method='POST')   (api.add_user)
    bottle.route('/users',   method='DELETE') (api.remove_user)
    bottle.route('/user',    method='GET')    (api.get_user)
    bottle.route('/user',    method='POST')   (api.update_user)
    bottle.route('/servers', method='GET')    (api.get_servers)
    bottle.route('/servers', method='POST')   (api.add_server)
    bottle.route('/servers', method='DELETE') (api.remove_server)
    bottle.route('/server',  method='PUT')    (api.get_server)
    bottle.route('/server',  method='POST')   (api.update_server)
    bottle.route('/index',   method='GET')    (api.get_indexes)
    bottle.route('/index',   method='POST')   (api.add_index)
    bottle.route('/index',   method='DELETE') (api.remove_index)
    bottle.route('/files',   method='PUT')    (api.get_files)
    bottle.route('/files',   method='POST')   (api.add_file)

    bottle.TEMPLATE_PATH.append('/people/r3boot/fileindexer/templates')
    api.run()

    return

if __name__ == '__main__':
    sys.exit(main())
