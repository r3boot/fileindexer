import bottle
import hashlib

class must_authenticate(object):
    def __init__(self):
        self.users = None
        self.servers = None
        self.__l = None

    def __call__(self, f):
        def decorator(*args, **kwargs):
            if not self.users:
                self.users = args[0].users
            if not self.servers:
                self.servers = args[0].servers
            if not self.__l:
                self.__l = args[0].logger

            (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))

            if username == '_server':
                """API key based auth"""
                server = self.servers.get(password)
                if not server:
                    self.__l.error('No server found for %s' % username)
                    bottle.abort(401, 'Access denied')
                server = server[0]
                user = self.users.get(server['username'])

            else:
                """User/pass based auth"""
                user = self.users.get(username)
                server = None
                if not user:
                    self.__l.error('No user found for %s' % username)
                    bottle.abort(401, 'Access denied')

                pwdhash = hashlib.sha512(password).hexdigest()
                if pwdhash != user['password']:
                    self.__l.error('Password mismatch')
                    bottle.abort(401, 'Access denied')

            return f(*args, username=user['username'], user=user, server=server, **kwargs)
        return decorator

class must_be_admin(object):
    def __init__(self):
        self.users = None

    def __call__(self, f):
        def decorator(*args, **kwargs):
            if not self.users:
                self.users = args[0].users

            (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))
            user = self.users.get(username)
            if user and 'is_admin' in user and user['is_admin']:
                return f(*args, **kwargs)
            else:
                bottle.abort(401, 'Access denied')
        return decorator


