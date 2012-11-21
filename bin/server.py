#!/usr/bin/env python

from gevent import monkey; monkey.patch_all()

import argparse
import base64
import bottle
import datetime
import json
import logging
import os
import pymongo
import sys
import uuid

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

class MongoAPI():
    __dbname = 'file_indexer'
    indexes = []

    def __init__(self, logger, collection_name, autoconnect=True, ):
        self.__l = logger
        self.collection_name = collection_name
        self.__conn = False
        self.__db = False
        self.collection = False

        if autoconnect:
            self.connect()
        self.create_indexes()

    def __destroy__(self):
        self.disconnect()

    def connect(self):
        if not self.__conn:
            try:
                self.__conn = pymongo.Connection()
            except:
                self.__l.debug('Failed to connect to mongodb')
                self.__conn = False
                return
            try:
                self.__db = self.__conn[self.__dbname]
            except:
                self.__l.debug('Failed to connect to %s' % self.__dbname)
                self.disconnect()
                return
            try:
                self.collection = self.__db[self.collection_name]
                self.__l.debug('Connected to %s.%s' % (self.__dbname, self.collection_name))
            except:
                self.__l.debug('Failed to connect to %s.%s' % (self.__dbname, self.collection_name))
                self.disconnect()
                return
        else:
            self.__l.debug('Already connected to mongodb')

    def disconnect(self):
        self.__conn.disconnect()
        self.__conn = False
        self.__db = False
        self.collection = False
        self.__l.debug('Disconnected from mongodb')

    def create_indexes(self):
        if not self.__db:
            self.__l.error('Not connected to mongodb')
            return False
        i = 0
        if len(self.indexes) > 0:
            for idx in self.indexes:
                self.collection.create_index(idx)
                i += 1
        self.__l.debug('Created %s indexes for %s.%s' % (i, self.__dbname, self.collection_name))

class Files(MongoAPI):
    indexes = ['path']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'files')
        self.__l = logger

    def get(self, path):
        result = self.collection.find({'path': path})
        return 'path' in result

    def add(self, meta):
        if not self.get(meta['path']):
            meta['last_modified'] = datetime.datetime.utcnow()
            self.collection.save(meta)
            self.__l.debug('%s stored' % meta['path'])
            return meta['_id']
        self.__l.debug('%s already in store' % meta['path'])

class Config(MongoAPI):
    __cfgclass = 'server'
    __defaults = {
        'paths': []
    }
    indexes = ['cfgclass']

    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'config')
        self.__l = logger
        self.__cfg = False

    def __getitem__(self, item):
        cfg = self.__get_config()
        if not cfg:
            self.__l.debug('No configuration found')
            return None

        if item in cfg.keys():
            return cfg[item]
        else:
            return None

    def __setitem__(self, item, value):
        cfg = self.__get_config()
        if not cfg:
            self.__l.debug('No configuration found')
            return False

        cfg[item] = value
        self.collection.save(cfg)
        return True

    def __get_config(self):
        self.__l.debug('Trying to retrieve configuration')
        cfg = self.collection.find_one({'cfgclass': self.__cfgclass})
        if cfg:
            self.__l.debug('Configuration found')
            (result, missing, unwanted) = self.validate(cfg)
            if not result:
                return False
        else:
            self.__l.debug('Failed to find configuration, creating defaults')
            self.set_defaults()

        return cfg

    def get_config(self):
        cfg = self.__get_config()
        del(cfg['_id'])
        return cfg

    def validate(self, cfg):
        self.__l.debug('Validating configuration')
        items = self.__defaults.keys()
        items.append('cfgclass')
        missing_in_cfg = []
        unwanted_in_cfg = []

        for k in cfg.keys():
            if k == '_id': continue
            if not k in items:
                unwanted_in_cfg.append(k)

        for k in items:
            if not k in cfg:
                missing_in_cfg.append(k)

        if missing_in_cfg:
            self.__l.debug('The following items are missing in the configuration:')
            for k in missing_in_cfg:
                self.__l.debug('* %s' % k)

        if unwanted_in_cfg:
            self.__l.debug('The following items are unwanted in the configuration:')
            for k in unwanted_in_cfg:
                self.__l.debug('* %s' % k)

        if missing_in_cfg or unwanted_in_cfg:
            self.__l.debug('Validation failed')
            return (False, missing_in_cfg, unwanted_in_cfg)
        else:
            self.__l.debug('Validation succeeded')
            return (True, missing_in_cfg, unwanted_in_cfg)

    def set_defaults(self):
        cfg = self.__defaults
        cfg['cfgclass'] = self.__cfgclass

        self.collection.save(cfg)

class Users(MongoAPI):
    indexes = ['username']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'users')
        self.__l = logger

    def list(self):
        users = []
        for user in self.collection.find():
            users.append(user['username'])
        return users

    def get(self, username):
        user = {}
        user_data = self.collection.find({'_id': username})
        for k,v in user_data[0].items():
            user[k] = v
        return user

    def add(self, meta):
        meta['_id'] = meta['username']
        return self.collection.save(meta)

    def remove(self, username):
        if username in self.list():
            self.collection.remove({'username': username})
            return True

class Servers(MongoAPI):
    indexes = ['servername']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'servers')
        self.__l = logger

    def list(self):
        servers = []
        for server in self.collection.find():
            servers.append(server['servername'])
        return servers

    def get(self, servername):
        server = {}
        server_data = self.collection.find({'_id': servername})
        for k,v in server_data[0].items():
            server[k] = v
        return server

    def add(self, meta):
        meta['_id'] = meta['servername']
        meta['apikey'] = str(uuid.uuid4())
        return self.collection.save(meta)

    def remove(self, servername):
        if servername in self.list():
            self.collection.remove({'servername': servername})
            return True
            

class API:
    __valid_config_items = ['paths']

    def __init__(self, logger, listen_ip, listen_port):
        self.__l = logger
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port
        self.config = Config(logger)
        self.files = Files(logger)
        self.users = Users(logger)
        self.servers = Servers(logger)

    def __deserialize(self, data):
        return json.loads(base64.b64decode(data))

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
