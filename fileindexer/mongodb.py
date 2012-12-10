import datetime
import hashlib
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
            try:
                self.collection.save(meta)
            except pymongo.connection.InvalidDocument, e:
                self.__l.error(e)
                self.__l.error(meta)
            self.__l.debug('%s stored' % meta['path'])
            return meta['_id']
        self.__l.debug('%s already in store' % meta['path'])

class Indexes(MongoAPI):
    indexes = ['path', 'username']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'indexes')
        self.__l = logger

    def list(self, username):
        indexes = []
        for idx in self.collection.find({'username': username}):
            indexes.append(idx)
        return indexes

    def get(self, username, path):
        idx = {}
        idx_data = self.collection.find({'username': username, 'path': path})
        try:
            for k,v in idx_data[0].items():
                idx[k] = v
        except IndexError:
            pass
        return idx

    def add(self, meta):
        return self.collection.save(meta)

    def update(self, meta):
        idx = self.get(meta['username'], meta['path'])
        for k,v in meta.items():
            if k == 'username': continue
            if k == 'path': continue
            idx[k] = v
        return self.collection.save(idx)

    def remove(self, username, path):
        if self.get(username, path):
            self.collection.remove({'username': username, 'path': path})
            return True

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

    def update(self, meta):
        user = self.get(meta['username'])
        for k,v in meta.items():
            if k == 'username': continue
            if k == 'new_password':
                password = hashlib.sha512(v).hexdigest()
                user['password'] =  password
            else:
                user[k] = v
        return self.collection.save(user)

    def remove(self, username):
        if username in self.list():
            self.collection.remove({'username': username})
            return True

class Servers(MongoAPI):
    indexes = ['hostname', 'apikey']
    def __init__(self, logger):
        MongoAPI.__init__(self, logger, 'servers')
        self.__l = logger

    def list(self):
        servers = []
        for server in self.collection.find():
            servers.append(server)
        return servers

    def get(self, apikey):
        servers = list(self.collection.find({'apikey': apikey}))
        return servers

    def get_by_username(self, username):
        servers = list(self.collection.find({'username': username}))
        return servers

    def add(self, meta):
        meta['_id'] = meta['hostname']
        meta['apikey'] = str(uuid.uuid4())
        return self.collection.save(meta)

    def remove(self, hostname):
        if hostname in self.list():
            self.collection.remove({'hostname': hostname})
            return True
