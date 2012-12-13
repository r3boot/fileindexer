
import json
import requests
import sys

class BackendClient():
    _username = '_server'

    def __init__(self, logger, backend, apikey):
        self.__l = logger
        self.__b = backend
        self.__k = apikey
        self.__s = requests.session()

    def __serialize(self, data):
        return json.dumps(data)

    def __request(self, method, path, payload={}):
        response = {}
        url = self.__b + path
        r = None
        if payload:
            payload = self.__serialize(payload)
        auth = requests.auth.HTTPBasicAuth(self._username, self.__k)
        try:
            if method == 'get':
                r = self.__s.get(url, auth=auth)
            elif method == 'post':
                r = self.__s.post(url, data=payload, auth=auth)
            elif method == 'delete':
                r = self.__s.delete(url, data=payload, auth=auth)
            else:
                self.__l.error('Invalid request method')
        except requests.exceptions.ConnectionError, e:
            r = False
            response['result'] = False
            response['message'] = e
            self.__l.error(e)
        finally:
            if r and r.status_code == 200:
                response = r.json
            else:
                response['result'] = False
                response['message'] = 'Request failed'

        return response

    def test_authentication(self, *args, **kwargs):
        response = self.__request(method='get', path='/auth')
        print(response)
        return response

    def get_users(self, *args, **kwargs):
        response = self.__request(method='get', path='/users')
        return response

    def get_user(self, username):
        response = self.__request(method='get', path='/users/%s' % username)
        return response

    def add_user(self, meta):
        payload = {'user': meta}
        response = self.__request(method='post', path='/users', payload=payload)
        return response

    def remove_user(self, username):
        response = self.__request(method='delete', path='/users/%s' % username)
        return response

    def get_servers(self):
        response = self.__request(method='get', path='/servers')
        return response

    def get_server(self, servername):
        response = self.__request(method='get', path='/servers/%s' % servername)
        return response

    def add_server(self, server):
        payload = {'server': server}
        response = self.__request(method='post', path='/servers', payload=payload)
        return response

    def remove_server(self, servername):
        response = self.__request(method='delete', path='/servers/%s' % servername)
        return response

    def query(self, meta):
        response = self.__request(method='post', path='/q', payload=meta)
        return response

if __name__ == '__main__':
    print('Dont call me directly')
    sys.exit(1)
