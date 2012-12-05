#!/usr/bin/env python

from gevent import monkey; monkey.patch_all()

import argparse
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
        self.files = fileindexer.mongodb.Files(logger)
        self.indexes = fileindexer.mongodb.Indexes(logger)
        self.users = fileindexer.mongodb.Users(logger)
        self.servers = fileindexer.mongodb.Servers(logger)

    def __deserialize(self, data):
        try:
            data = eval(json.loads(data))
        except NameError, e:
            self.__l.error(e)
            self.__l.debug(data)

        if len(data) > 0:
            print(data)
            for k,v in data.items():
                self.__l.debug('%s: %s' % (k, v))
        return data

    def __get_username(self):
        (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))
        return username

    def run(self):
        bottle.run(host=self.__listen_ip, port=self.__listen_port, server='gevent')

    def webapp(self):
        return bottle.jinja2_template('index.html')

    def serve_js(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/js/%s' % filename):
            return open('/people/r3boot/fileindexer/js/%s' % filename, 'r').read()
        else:
            bottle.abort(404, 'File not found')

    def serve_css(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/css/%s' % filename):
            bottle.response.set_header('Content-type', 'text/css')
            return open('/people/r3boot/fileindexer/css/%s' % filename, 'r').read()
        else:
            bottle.abort(404, 'File not found')

    def ping(self):
        return {'result': True, 'message': 'pong'}

    @fileindexer.decorators.must_authenticate()
    def test_authentication(self):
        return {'result': True, 'message': 'authenticated'}

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

    @fileindexer.decorators.must_authenticate()
    def get_indexes(self, username):
        indexes = []
        for idx in self.indexes.list(username):
            del(idx['_id'])
            indexes.append(idx)
        
        if indexes:
            return {'result': True, 'indexes': indexes}
        else:
            return {'result': False, 'message': 'No indexes found'}

    @fileindexer.decorators.must_authenticate()
    def get_index(self, username):
        username = self.__get_username()
        if username != self.__get_username():
            bottle.abort(401, 'Access denied')
        idx = self.index.get(request['username'], request['path'])
        if idx:
            return {'result': True, 'index': idx}
        else:
            return {'result': False, 'message': 'Failed to retrieve index'}

    @fileindexer.decorators.must_authenticate()
    def update_index(self, username):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        self.indexes.update(request)
        return {'result': True, 'message': 'Index updated'}

    @fileindexer.decorators.must_authenticate()
    def add_index(self, username):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        if 'path' in request:
            self.indexes.add(request)
            return {'result': True, 'message': 'Path %s added to indexes' % request['path']}
        else:
            return {'result': False, 'message': 'No index info received'}

    @fileindexer.decorators.must_authenticate()
    def remove_index(self, username):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        if self.index.remove(request):
            return {'result': True, 'message': 'User removed succesfully'}
        else:
            return {'result': True, 'message': 'Failed to remove user'}

    @fileindexer.decorators.must_authenticate()
    @fileindexer.decorators.must_be_admin()
    def get_users(self):
        users = self.users.list()
        if users:
            return {'result': True, 'users': users}
        else:
            return {'result': False, 'message': 'No users found'}

    @fileindexer.decorators.must_authenticate()
    def get_user(self, username):
        user = self.users.get(username)
        if user:
            return {'result': True, 'user': user}
        else:
            return {'result': False, 'message': 'Failed to retrieve userdata'}

    @fileindexer.decorators.must_authenticate()
    def update_user(self, username):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        self.users.update(request)
        return {'result': True, 'message': 'User profile updated'}

    @fileindexer.decorators.must_authenticate()
    @fileindexer.decorators.must_be_admin()
    def add_user(self):
        request = self.__deserialize(bottle.request.body.readline())
        if 'user' in request:
            return {'result': True, 'message': self.users.add(request['user'])}
        else:
            return {'result': False, 'message': 'No userinfo received'}

    @fileindexer.decorators.must_authenticate()
    @fileindexer.decorators.must_be_admin()
    def remove_user(self, username):
        if self.users.remove(username):
            return {'result': True, 'message': 'User removed succesfully'}
        else:
            return {'result': True, 'message': 'Failed to remove user'}

    @fileindexer.decorators.must_authenticate()
    def get_servers(self, username):
        servers = self.servers.list()
        if servers:
            return {'result': True, 'servers': servers}
        else:
            return {'result': False, 'message': 'No servers defined'}

    @fileindexer.decorators.must_authenticate()
    def get_server(self, server):
        server = self.servers.get(server)
        if server:
            return {'result': True, 'server': server}
        else:
            return {'result': False, 'message': 'Failed to retrieve server'}

    @fileindexer.decorators.must_authenticate()
    def add_server(self, username):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        if 'hostname' in request:
            return {'result': True, 'message': self.servers.add(request)}
        else:
            return {'result': False, 'message': 'Failed to add server'}

    @fileindexer.decorators.must_authenticate()
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
    bottle.route('/ping',                  method='GET')    (api.ping)
    bottle.route('/auth',                  method='GET')    (api.test_authentication)
    bottle.route('/users',                 method='GET')    (api.get_users)
    bottle.route('/users',                 method='POST')   (api.add_user)
    bottle.route('/users/:username',       method='GET')    (api.get_user)
    bottle.route('/users/:username',       method='POST')   (api.update_user)
    bottle.route('/users/:username',       method='DELETE') (api.remove_user)
    bottle.route('/servers/:username',     method='GET')    (api.get_servers)
    bottle.route('/servers/:username',     method='POST')   (api.add_server)
    bottle.route('/servers/:server',       method='GET')    (api.get_server)
    bottle.route('/servers/:server',       method='DELETE') (api.remove_server)
    bottle.route('/index/:username',       method='GET')    (api.get_indexes)
    bottle.route('/index/:username',       method='POST')   (api.add_index)
    bottle.route('/index',                 method='DELETE') (api.remove_index)
    bottle.route('/files',                 method='GET')    (api.get_files)
    bottle.route('/files',                 method='POST')   (api.add_file)

    bottle.TEMPLATE_PATH.append('/people/r3boot/fileindexer/templates')
    api.run()

    return

if __name__ == '__main__':
    sys.exit(main())
