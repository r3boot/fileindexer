import datetime
import pymongo
import uuid

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
        try:
            for k,v in user_data[0].items():
                user[k] = v
        except IndexError:
            pass
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
