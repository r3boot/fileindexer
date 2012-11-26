#!/usr/bin/env python

from gevent import monkey; monkey.patch_all()

import argparse
import base64
import bottle
import json
import logging
import os
import sys

sys.path.append('/people/r3boot/fileindexer')

import fileindexer.decorators
import fileindexer.mongodb

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

class API:
    __valid_config_items = ['paths']
    users = None

    def __init__(self, logger, listen_ip, listen_port):
        self.__l = logger
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port
        self.config = fileindexer.mongodb.Config(logger)
        self.files = fileindexer.mongodb.Files(logger)
        self.users = fileindexer.mongodb.Users(logger)
        self.servers = fileindexer.mongodb.Servers(logger)

    def __deserialize(self, data):
        return json.loads(base64.urlsafe_b64decode(data))

    def run(self):
        bottle.run(host=self.__listen_ip, port=self.__listen_port, server='gevent')

    def webapp(self):
        return bottle.jinja2_template('index.html')

    def serve_js(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/js/%s' % filename):
            return open('/people/r3boot/fileindexer/js/%s' % filename, 'r').read()

    def serve_css(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/css/%s' % filename):
            return open('/people/r3boot/fileindexer/css/%s' % filename, 'r').read()

    def ping(self):
        return {'result': True, 'message': 'pong'}

    @fileindexer.decorators.must_authenticate()
    def test_authentication(self):
        return {'result': True, 'message': 'authenticated'}

    def get_config(self):
        config = self.config.get_config()
        if config:
            return {'result': True, 'config': config}
        else:
            return {'result': False, 'message': 'Failed to retrieve configuration'}

    def set_config(self, key):
        if key in self.__valid_config_items:
            request = self.__deserialize(bottle.request.body.readline())
            if 'value' in request:
                self.config[key] = request['value']
                return {'result': True, key: request['value']}
            else:
                return {'result': False, 'message': 'Failed to set configuration item'}
        else:
            return {'result': False, 'message': 'Not a valid configuration item'}

    def get_files(self):
        try:
            request = self.__deserialize(bottle.request.body.readline())
        except ValueError:
            request = {}
        config = self.config.get_config()
        if 'root' in request:
            return {'result': False, 'message': 'FNI'}
        else:
            return {'result': True, 'files': config['paths']}

    def add_file(self):
        request = self.__deserialize(bottle.request.body.readline())
        if 'meta' in request:
            _id = self.files.add(request['meta'])
            return {'result': True, '_id': _id}
        else:
            return {'result': False, 'message': 'Failed to retrieve metadata'}

    def get_users(self):
        users = self.users.list()
        if users:
            return {'result': True, 'users': users}
        else:
            return {'result': False, 'message': 'No users found'}

    def get_user(self, username):
        user = self.users.get(username)
        if user:
            return {'result': True, 'user': user}
        else:
            return {'result': False, 'message': 'Failed to retrieve userdata'}

    def add_user(self):
        request = self.__deserialize(bottle.request.body.readline())
        if 'user' in request:
            return {'result': True, 'message': self.users.add(request['user'])}
        else:
            return {'result': False, 'message': 'No userinfo received'}

    def remove_user(self, username):
        if self.users.remove(username):
            return {'result': True, 'message': 'User removed succesfully'}
        else:
            return {'result': True, 'message': 'Failed to remove user'}

    def get_servers(self):
        servers = self.servers.list()
        if servers:
            return {'result': True, 'servers': servers}
        else:
            return {'result': False, 'message': 'No servers defined'}

    def get_server(self, server):
        server = self.servers.get(server)
        if server:
            return {'result': True, 'server': server}
        else:
            return {'result': False, 'message': 'Failed to retrieve server'}

    def add_server(self):
        request = self.__deserialize(bottle.request.body.readline())
        if 'server' in request:
            return {'result': True, 'message': self.servers.add(request['server'])}
        else:
            return {'result': False, 'message': 'Failed to add server'}

    def remove_server(self, server):
        if self.servers.remove(server):
            return {'result': True, 'message': 'Server removed successfully'}
        else:
            return {'result': False, 'message': 'Failed to remove server'}

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

    ## API
    bottle.route('/ping',            method='GET')    (api.ping)
    bottle.route('/auth',            method='GET')    (api.test_authentication)
    bottle.route('/config',          method='GET')    (api.get_config)
    bottle.route('/config/:key',     method='POST')   (api.set_config)
    bottle.route('/users',           method='GET')    (api.get_users)
    bottle.route('/users',           method='POST')   (api.add_user)
    bottle.route('/users/:username', method='GET')    (api.get_user)
    bottle.route('/users/:username', method='DELETE') (api.remove_user)
    bottle.route('/servers',         method='GET')    (api.get_servers)
    bottle.route('/servers',         method='POST')   (api.add_server)
    bottle.route('/servers/:server', method='GET')    (api.get_server)
    bottle.route('/servers/:server', method='DELETE') (api.remove_server)
    bottle.route('/files',           method='GET')    (api.get_files)
    bottle.route('/files',           method='POST')   (api.add_file)

    bottle.TEMPLATE_PATH.append('/people/r3boot/fileindexer/templates')
    api.run()

    return

if __name__ == '__main__':
    sys.exit(main())
