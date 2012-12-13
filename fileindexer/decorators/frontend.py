import bottle

class must_authenticate(object):
    def __init__(self):
        self.backend = None
        self.__l = None

    def __call__(self, f):
        def decorator(*args, **kwargs):
            if not self.backend:
                self.backend = args[0].backend
            if not self.__l:
                self.__l = args[0].logger

            (username, password) = bottle.parse_auth(bottle.request.get_header('Authorization'))

            response = self.backend.test_authentication()
            if response['result']:
                self.__l.debug('Authentication succeeded for %s' % username)
                return f(*args, username=username, **kwargs)
            else:
                self.__l.warn('Authentication failed for %s' % username)
                bottle.abort(401, 'Access denied')

            return f(*args, username=username, **kwargs)
        return decorator
