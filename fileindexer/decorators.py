import bottle
import hashlib

class must_authenticate(object):
    def __init__(self):
        self.users = None

    def __call__(self, f):
        def decorator(*args, **kwargs):
            if not self.users:
                self.users = args[0].users

            (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))
            user = self.users.get(username)
            if not user:
                bottle.abort(401, 'Access denied')
            if len(user) != 4:
                bottle.abort(401, 'Access denied')
            pwdhash = hashlib.sha512(password).hexdigest()
            if pwdhash != user['password']:
                bottle.abort(401, 'Access denied')
            return f(*args, **kwargs)
        return decorator
