#!/usr/bin/env python

import argparse
import bottle
import datetime
import json
import logging
import os
import pymongo
import sys

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

    def __init__(self, logger, collection_name, autoconnect=True, ):
        self.__l = logger
        self.collection_name = collection_name
        self.__conn = False
        self.__db = False
        self.collection = False

        if autoconnect:
            self.connect()

    def __destroy__(self):
        self.disconnect()

    def connect(self):
        if not self.__conn:
            try:
                self.__conn = pymongo.Connection()
                self.__l.debug('Connected to mongodb')
            except:
                self.__l.debug('Failed to connect to mongodb')
                self.__conn = False
                return
            try:
                self.__db = self.__conn[self.__dbname]
                self.__l.debug('Connected to db %s' % self.__dbname)
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

class Files(MongoAPI):
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
            return True
        self.__l.debug('%s already in store' % meta['path'])

class Config(MongoAPI):
    __cfgclass = 'server'
    __defaults = {
        'paths': []
    }

    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'config')
        self.__l = logger
        self.__cfg = False

    def __getitem__(self, item):
        cfg = self.get_config()
        if not cfg:
            self.__l.debug('No configuration found')
            return None

        if item in cfg.keys():
            return cfg[item]
        else:
            return None

    def __setitem__(self, item, value):
        cfg = self.get_config()
        if not cfg:
            self.__l.debug('No configuration found')
            return False

        cfg[item] = value
        self.collection.save(cfg)
        return True

    def get_config(self):
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

class API:
    def __init__(self, logger, listen_ip, listen_port):
        self.__l = logger
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port
        self.config = Config(logger)
        self.files = Files(logger)
        bottle.TEMPLATE_PATH.append('/people/r3boot/fileindexer/templates')
    """
    def dispatcher(self):
        response = {}
        request = bottle.request.body.read()
        print('request: ' + request)
        if not isinstance(request, dict):
            response['result'] = False
            response['error'] = 'request is not a dictionary'
        elif not 'method' in request:
            response['result'] = False
            response['error'] = 'no method requested'

        elif request['method'] == 'ping':
            response['result'] = True
            response['error'] = 'pong'

        elif request['method'] == 'config.get':
            if 'item' in request:
                value = self.config[request['item']]
                if value != None:
                    response['result'] = True
                    response['value'] = value
                else:
                    response['result'] = False
                    response['error'] = 'config.get[%s] not found' % request['item']
            else:
                response['result'] = False
                response['error'] = 'config.get requires an item'

        elif request['method'] == 'config.set':
            if not 'item' in request:
                response['result'] = False
                response['error'] = 'config.set requires an item'
            elif not 'value' in request:
                response['result'] = False
                response['error'] = 'config.set requires a value'
            else:
                self.config[request['item']] = request['value']
                response['result'] = True

        elif request['method'] == 'file.add':
            if not 'meta' in request:
                response['result'] = False
                response['error'] = 'no metadata defined'
            elif not 'path' in request['meta']:
                response['result'] = False
                response['error'] = 'no path defined'
            elif not 'parent' in request['meta']:
                response['result'] = False
                response['error'] = 'no parent defined'
            else:
                result = self.files.add(request['meta'])
                response['result'] = result
                if not result:
                    response['error'] = 'failed to add'
        else:
            response['result'] = False
            response['error'] = 'unknown request'

        self.__l.debug(response)
        #self.__l.debug(self.__serialize(response))
        #bottle.response.set_header('Content-Type', 'application/x-www-form-urlencoded')
        #return {'result': True}
        return response
    """
    def webapp(self):
        return bottle.jinja2_template('index.html')

    def serve_js(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/js/%s' % filename):
            return open('/people/r3boot/fileindexer/js/%s' % filename, 'r').read()

    #def options(self):
    #    bottle.response.status = 200
    #    bottle.response.add_header('Allow', 'GET, POST, OPTIONS')
    #    bottle.response.add_header('Access-Control-Allow-Origin', '*')
    #    bottle.response.add_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
    #    bottle.response.add_header('Content-Length', '0')
    #    return {}

    def get_files(self):
        return {}

    def run(self):
        bottle.run(host=self.__listen_ip, port=self.__listen_port)

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
    bottle.route('/', method='GET')(api.webapp)
    bottle.route('/js/:filename', method='GET')(api.serve_js)
    #bottle.route('/files', method='OPTIONS')(api.options)
    bottle.route('/files', method='GET')(api.get_files)
    api.run()

    return

if __name__ == '__main__':
    sys.exit(main())
