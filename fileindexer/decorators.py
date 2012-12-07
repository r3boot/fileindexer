import bottle
import hashlib

class must_authenticate(object):
    def __init__(self):
        self.users = None
        self.servers = None

    def __call__(self, f):
        def decorator(*args, **kwargs):
            if not self.users:
                self.users = args[0].users
            if not self.servers:
                self.servers = args[0].servers

            (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))
            user = self.users.get(username)
            servers = self.servers.get(username)
            server = None

            if not user and not servers:
                bottle.abort(401, 'Access denied')
            if username != user['username']:
                print("username != user[username]")
                bottle.abort(401, 'Access denied')
            found_key = False
            for s in servers:
                if password == s['apikey']:
                    server = s
                    found_key = True
            if not found_key:
                pwdhash = hashlib.sha512(password).hexdigest()
                if pwdhash == user['password']:
                     found_key = True
            if not found_key:
                print("not found_key")
                bottle.abort(401, 'Access denied')
            return f(*args, server=server, **kwargs)
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


