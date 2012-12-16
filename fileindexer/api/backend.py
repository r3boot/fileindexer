import bottle
import datetime
import json

from fileindexer.decorators.backend import must_authenticate, must_be_admin
from fileindexer.backends.mongodb import Users, Servers

class BackendAPI:
    __valid_config_items = ['paths']
    users = None

    def __init__(self, logger, listen_ip, listen_port, write_queue):
        self.logger = logger
        self.__l = logger
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port
        self.__wq = write_queue
        self.users = Users(logger)
        self.servers = Servers(logger)

    def __deserialize(self, data):
        try:
            data = json.loads(data)
        except NameError, e:
            self.__l.error(e)
            self.__l.debug(data)

        #if len(data) > 0:
        #    for k,v in data.items():
        #        self.__l.debug('%s: %s' % (k, v))
        return data

    def __get_username(self):
        (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))
        return username

    def run(self):
        bottle.run(host=self.__listen_ip, port=self.__listen_port, server='gevent')

    def ping(self):
        return {'result': True, 'message': 'pong'}

    @must_authenticate()
    def test_authentication(self, *args, **kwargs):
        return {'result': True, 'message': 'authenticated'}

    @must_authenticate()
    @must_be_admin()
    def get_users(self, *args, **kwargs):
        users = self.users.list()
        if users:
            return {'result': True, 'users': users}
        else:
            return {'result': False, 'message': 'No users found'}

    @must_authenticate()
    def get_user(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            return {'result': True, 'user': user}
        else:
            return {'result': False, 'message': 'Failed to retrieve userdata'}

    @must_authenticate()
    def update_user(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        self.users.update(request)
        return {'result': True, 'message': 'User profile updated'}

    @must_authenticate()
    @must_be_admin()
    def add_user(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'user' in request:
            return {'result': True, 'message': self.users.add(request['user'])}
        else:
            return {'result': False, 'message': 'No userinfo received'}

    @must_authenticate()
    @must_be_admin()
    def remove_user(self, *args, **kwargs):
        username = args[0]
        if self.users.remove(username):
            return {'result': True, 'message': 'User removed succesfully'}
        else:
            return {'result': True, 'message': 'Failed to remove user'}

    @must_authenticate()
    def add_document(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        for item in request:
            for dt in ['atime', 'ctime', 'mtime']:
                item[dt] = datetime.datetime.fromtimestamp(float(item[dt]))
            self.__wq.put(item, block=False, timeout=0.1)
        return {'result': True, 'message': 'Document added successfully'}

    def query(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'query' in request:
            self.__l.debug('Q: %s' % request['query'])
            r = self.wwm.query(request['query'])
            documents = []
            for doc in r['documents']:
                for k,v in doc.items():
                    if isinstance(v, datetime.datetime):
                        doc[k] = v.isoformat()
                    else:
                        doc[k] = v
                documents.append(doc)
            r['documents'] = documents
            return {'result': True, 'results': r}
