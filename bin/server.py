#!/usr/bin/env python

import argparse
import base64
import bottle
import json
import logging
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

    def get(self, q):
        return self.collection.find(q)

    def add(self, meta):
        if not self.get({'path_sha1': meta['path_sha1']}):
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
            return False

        if item in cfg.keys():
            return cfg[item]
        else:
            return False

    def __setitem__(self, item, value):
        cfg = self.get_config()
        if not cfg:
            self.__l.debug('No configuration found')
            return False

        cfg[item] = value
        self.collection.save(cfg)

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
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port
        self.config = Config(logger)
        self.files = Files(logger)

    def __serialize(self, data):
        return base64.b64encode(json.dumps(data))

    def __deserialize(self, data):
        return json.loads(base64.b64decode(data))

    def ping(self):
        return self.__serialize('pong')

    def cfg_get(self, item):
        return self.__serialize(self.config[item])

    def cfg_set(self, item, value):
        self.config[item] = self.__deserialize(value)
        return self.__serialize('ok')

    def add_file(self, data):
        result = self.files.add(self.__deserialize(data))
        if result:
            return self.__serialize('ok')
        else:
            return self.__serialize('failed')

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
    bottle.route('/ping')(api.ping)
    bottle.route('/cfg/get/:item')(api.cfg_get)
    bottle.route('/cfg/set/:item/:value')(api.cfg_set)
    bottle.route('/file/add/:data')(api.add_file)
    api.run()

    return

if __name__ == '__main__':
    sys.exit(main())
