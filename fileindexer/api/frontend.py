import bottle
import json
import os

from fileindexer.decorators.frontend import must_authenticate

class FrontendAPI:
    __valid_config_items = ['paths']
    users = None

    def __init__(self, logger, listen_ip, listen_port, backend):
        self.logger = logger
        self.backend = backend
        self.__l = logger
        self.__listen_ip = listen_ip
        self.__listen_port = listen_port

    def __deserialize(self, data):
        try:
            data = json.loads(data)
        except NameError, e:
            self.__l.error(e)
            self.__l.debug(data)

        if len(data) > 0:
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

    def serve_png(self, filename):
        if os.path.exists('/people/r3boot/fileindexer/img/%s' % filename):
            bottle.response.set_header('Content-type', 'image/png')
            return open('/people/r3boot/fileindexer/img/%s' % filename, 'r').read()
        else:
            bottle.abort(404, 'File not found')

    def ping(self):
        return {'result': True, 'message': 'pong'}

    @must_authenticate()
    def test_authentication(self, *args, **kwargs):
        response = self.backend.test_authentication(*args, **kwargs)
        return response
            
    def get_files(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'parent' in request:
            files = []
            for f in self.files.get(request['parent']):
                f['last_modified'] = f['last_modified'].isoformat()
                files.append(f)
            return {'result': True, 'files': files}
        else:
            return {'result': False, 'message': 'invalid index'}

    def add_file(self):
        request = self.__deserialize(bottle.request.body.readline())
        if 'meta' in request:
            _id = self.files.add(request['meta'])
            return {'result': True, '_id': _id}
        else:
            return {'result': False, 'message': 'Failed to retrieve metadata'}

    @must_authenticate()
    def get_indexes(self, *args, **kwargs):
        username = kwargs['username']
        indexes = []
        for idx in self.indexes.list(username):
            del(idx['_id'])
            indexes.append(idx)
        
        if indexes:
            return {'result': True, 'indexes': indexes}
        else:
            return {'result': False, 'message': 'No indexes found'}

    @must_authenticate()
    def get_index(self, *args, **kwargs):
        username = kwargs['username']
        request = self.__deserialize(bottle.request.body.readline())
        idx = self.index.get(username, request['path'])
        if idx:
            return {'result': True, 'index': idx}
        else:
            return {'result': False, 'message': 'Failed to retrieve index'}

    @must_authenticate()
    def update_index(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        username = self.__get_username()
        if request['username'] != username:
            bottle.abort(401, 'Access denied')
        self.indexes.update(request)
        return {'result': True, 'message': 'Index updated'}

    @must_authenticate()
    def add_index(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        username = kwargs['username']
        server = kwargs['server']
        request['username'] = username
        request['server'] = server['hostname']
        if 'path' in request:
            if self.indexes.add(request):
                return {'result': True, 'message': 'Path %s added to indexes' % request['path']}
            else:
                return {'result': False, 'message': 'Failed to add %s' % request['path']}
        else:
            return {'result': False, 'message': 'No index info received'}

    @must_authenticate()
    def remove_index(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        username = kwargs['username']
        if self.indexes.remove(username, request['path']):
            return {'result': True, 'message': 'Index removed succesfully'}
        else:
            return {'result': False, 'message': 'Failed to remove index'}

    @must_authenticate()
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
    def add_user(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'user' in request:
            return {'result': True, 'message': self.users.add(request['user'])}
        else:
            return {'result': False, 'message': 'No userinfo received'}

    @must_authenticate()
    def remove_user(self, *args, **kwargs):
        username = args[0]
        if self.users.remove(username):
            return {'result': True, 'message': 'User removed succesfully'}
        else:
            return {'result': True, 'message': 'Failed to remove user'}

    @must_authenticate()
    def get_servers(self, *args, **kwargs):
        servers = self.servers.list()
        if servers:
            return {'result': True, 'servers': servers}
        else:
            return {'result': False, 'message': 'No servers defined'}

    @must_authenticate()
    def get_server(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'hostname' in request:
            server = self.servers.get_by_hostname(request['hostname'])
        if server:
            return {'result': True, 'server': server}
        else:
            return {'result': False, 'message': 'Failed to retrieve server'}

    @must_authenticate()
    def add_server(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'hostname' in request:
            return {'result': True, 'message': self.servers.add(request)}
        else:
            return {'result': False, 'message': 'Failed to add server'}

    @must_authenticate()
    def update_server(self, *args, **kwargs):
        return {'result': False, 'message': 'FNI'}

    @must_authenticate()
    def remove_server(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'hostname' in request:
            self.servers.remove(request['hostname'])
            return {'result': True, 'message': 'Server removed successfully'}
        else:
            return {'result': False, 'message': 'Invalid request'}

    def query(self, *args, **kwargs):
        request = self.__deserialize(bottle.request.body.readline())
        if 'query' in request:
            response = self.backend.query(request)
            return response
        else:
            return {'result': False, 'message': 'Invalid request'}
