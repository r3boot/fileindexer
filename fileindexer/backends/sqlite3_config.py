import hashlib
import sqlite3
import uuid

REDIS_USERS_DB = 0
REDIS_SERVERS_DB = 1

class Sqlite3Config():
    def __init__(self, logger, db='config', basedir='/fileindexer'):
        self.__l = logger
        self.__conn = sqlite3.connect('%s/%s.db' % (basedir, db))
        self.__c = self.__conn.cursor()

    def __destroy__(self):
        if self.__conn:
            self.__conn.close()

    def has_table(self, name):
        fmtname = (name, )
        self.__c.execute('SELECT name FROM sqlite_master WHERE type = \"table\" and name = ?', fmtname)
        result = self.__c.fetchone()
        if result:
            return True

    def execute(self, sql, fmtitems=None):
        if fmtitems:
            if not isinstance(fmtitems, tuple):
                fmtitems = (fmtitems, )
            self.__c.execute(sql, fmtitems)
        else:
            self.__c.execute(sql)
        return self.__c.fetchall()

class Users(Sqlite3Config):
    _create_table_sql = 'CREATE TABLE users (username text, password text, realname text, is_admin integer)'
    _salt = '2aaa4b761c70d07c80b858aa423260e95cd68e02'
    _default_users = [{
        'username': 'admin',
        'password': hashlib.sha256('%s admin' % _salt).hexdigest(),
        'realname': 'Default administrative account',
        'is_admin': True
    }]

    def __init__(self, logger):
        Sqlite3Config.__init__(self, logger)
        self.__l = logger
        self.initialize()

    def initialize(self):
        if not self.has_table('users'):
            self.execute(self._create_table_sql)

        for user in self._default_users:
            username = user['username']
            if len(self.execute('SELECT username FROM users WHERE username = ?', username)) == 0:
                self.add(user)

    def validate_password(self, username, password):
        if username in self.list():
            user = self.get(username)
            pwdhash = hashlib.sha256('%s %s' % (self._salt, password)).hexdigest()
            return pwdhash == user['password']

    def list(self):
        return [row[0] for row in self.execute('SELECT username FROM users')]

    def get(self, username):
        user = {}
        result = self.execute('SELECT username,password,realname,is_admin FROM users WHERE username = ?', username)
        if len(result) != 1:
            self.__l.warn('Users.get: len(result) != 1')
            return user

        r = result[0]
        user['username'] = r[0]
        user['password'] = r[1]
        user['realname'] = r[2]
        user['is_admin'] = r[3]
        return user

    def add(self, meta):
        self.__l.debug('Adding user %s' % meta['username'])
        fmtitems = (meta['username'], meta['password'], meta['realname'], meta['is_admin'], )
        self.execute('INSERT INTO users VALUES (?,?,?,?)', fmtitems)

    def update(self, meta):
        current_meta = self.get(meta['username'])
        if len(current_meta) == 0:
            return

        for k,v in meta.items():
            if k == 'username': continue
            if k == 'new_password':
                new_pass = '%s %s' % (self._salt, v)
                password = hashlib.sha512(new_pass).hexdigest()
                k = 'password'
                v = password
            if meta[k] != current_meta[k]:
                self.__l.debug('Updating %s.%s: %s -> %s' % (meta['username'], k, current_meta[k], v))
                fmtitems = (k, v, k, current_meta[k], )
                self.execute('UPDATE users SET ? = ? WHERE ? = ?', fmtitems)

    def remove(self, username):
        if username in self.list():
            self.execute('DELETE FROM users WHERE username = ?', username)
            self.__l.info('User %s removed' % username)
            return True
        self.__l.info('No such user %s' % username)
