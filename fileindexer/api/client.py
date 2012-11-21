
import base64
import json
import requests
import sys

class APIClient():
    def __init__(self, logger, host, port):
        self.__l = logger
        self.__uri = 'http://%s:%s' % (host, port)
        self.__s = requests.session()

    def __serialize(self, data):
        return base64.b64encode(json.dumps(data))

    def __request(self, method, path, payload={}):
        response = {}
        url = self.__uri + path
        r = None
        if payload:
            payload = self.__serialize(payload)
        try:
            if method == 'get':
                r = self.__s.get(url)
            elif method == 'post':
                r = self.__s.post(url, data=payload)
            elif method == 'delete':
                r = self.__s.delete(url)
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

    def ping(self):
        response = self.__request(method='get', path='/ping')
        return response['result']

    def get_config(self):
        response = self.__request(method='get', path='/config')
        if response['result']:
            return response['config']
        else:
            self.__l.error(response['message'])
            return {}

    def set_config(self, key, value):
        payload = {'value': value}
        response = self.__request(method='post', path='/config/%s' % key, payload=payload)
        return response['result']

    def add_file(self, meta):
        payload = {'meta': meta}
        response = self.__request(method='post', path='/files', payload=payload)
        return response['result']

    def get_users(self):
        response = self.__request(method='get', path='/users')
        if response['result'] and 'users' in response:
            return response['users']
        else:
            self.__l.error('No users received')

    def get_user(self, username):
        response = self.__request(method='get', path='/users/%s' % username)
        if response['result'] and 'user' in response:
            return response['user']
        else:
            self.__l.error('No user received')

    def add_user(self, meta):
        payload = {'user': meta}
        response = self.__request(method='post', path='/users', payload=payload)
        return response['result']

    def remove_user(self, username):
        response = self.__request(method='delete', path='/users/%s' % username)
        return response['result']

    def get_servers(self):
        response = self.__request(method='get', path='/servers')
        if response['result'] and 'servers' in response:
            return response['servers']
        else:
            return response['result']

    def get_server(self, servername):
        response = self.__request(method='get', path='/servers/%s' % servername)
        return response['server']

    def add_server(self, server):
        payload = {'server': server}
        response = self.__request(method='post', path='/servers', payload=payload)
        return response['result']

    def remove_server(self, servername):
        response = self.__request(method='delete', path='/servers/%s' % servername)
        return response['result']

if __name__ == '__main__':
    print('Dont call me directly')
    sys.exit(1)
