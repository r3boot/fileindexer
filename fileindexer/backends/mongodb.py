import hashlib
import pymongo
import uuid

class MongoAPI():
    __dbname = 'fileindexer'
    indexes = []

    def __init__(self, logger, collection_name, autoconnect=True):
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

class Users(MongoAPI):
    _salt = '2aaa4b761c70d07c80b858aa423260e95cd68e02'
    _default_users = [{
        'username': 'admin',
        'password': hashlib.sha256('%s admin' % _salt).hexdigest(),
        'realname': 'Default administrative account',
        'is_admin': True
    }]
    indexes = ['username']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'users')
        self.__l = logger
        self.initialize()

    def initialize(self):
        if len(self.list()) == 0:
            self.__l.info('No users found, creating default user(s)')
            for user in self._default_users:
                self.add(user)

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
        result = self.collection.save(meta)
        if result:
            self.__l.info('Added user %s' % meta['username'])
        else:
            self.__l.warn('Failed to add user %s' % meta['username'])
        return result

    def update(self, meta):
        user = self.get(meta['username'])
        for k,v in meta.items():
            if k == 'username': continue
            if k == 'new_password':
                new_pass = '%s %s' % (self._salt, v)
                password = hashlib.sha512(new_pass).hexdigest()
                user['password'] =  password
            else:
                user[k] = v
        return self.collection.save(user)

    def remove(self, username):
        if username in self.list():
            result = self.collection.remove({'username': username})
            if result:
                self.__l.info('User %s removed' % username)
                return True
            else:
                self.__l.warn('Failed to remove user %s' % username)
        else:
            self.__l.info('No such user %s' % username)

class Servers(MongoAPI):
    indexes = ['hostname', 'apikey']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'servers')
        self.__l = logger
        self.initialize()

    def initialize(self):
        if len(self.list()) == 0:
            meta = {'hostname': '_crawler', 'username': 'admin', 'apikey': str(uuid.uuid4())}
            self.add(meta)
            self.__l.info('Generated api key for crawler: %s' % meta['apikey'])

            meta = {'hostname': '_frontend', 'username': 'admin', 'apikey': str(uuid.uuid4())}
            self.add(meta)
            self.__l.info('Generated api key for frontend: %s' % meta['apikey'])

    def list(self):
        servers = list(self.collection.find())
        return servers

    def get(self, apikey):
        servers = list(self.collection.find({'apikey': apikey}))
        return servers

    def get_by_username(self, username):
        servers = list(self.collection.find({'username': username}))
        return servers

    def get_by_hostname(self, hostname):
        servers = list(self.collection.find({'hostname': hostname}))
        return servers

    def add(self, meta):
        meta['_id'] = meta['hostname']
        meta['apikey'] = str(uuid.uuid4())
        return self.collection.save(meta)

    def remove(self, hostname):
        return self.collection.remove({'hostname': hostname})
