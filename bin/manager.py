#!/usr/bin/env python

import argparse
import getpass
import hashlib
import logging
import sys

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.api.client import APIClient as API

__description__ = 'Add description'

_d_debug = False
_d_host = '127.0.0.1'
_d_port = 5423
_d_list_users = False
_d_list_user = False
_d_realname = None
_d_add_server = False
_d_remove_server = False
_d_list_server = False
_d_list_servers = False
_d_owner = False
_d_protocols = []

ll2str = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-D', dest='debug', action='store_true',
        default=_d_debug, help='Enable debugging')

    parser.add_argument('-H', dest='host', action='store',
        default=_d_host, help='Host to connect to, defaults to %s' % _d_host)
    parser.add_argument('-P', dest='port', action='store',
        default=_d_port, help='Port to connect to, defaults to %s' % _d_port)

    user_group = parser.add_argument_group('users')
    user_group.add_argument('--list-users', dest='list_users', action='store_true',
        default=_d_list_users, help='List all users')
    user_group.add_argument('--list-user', dest='list_user', action='store',
        default=_d_list_user, help='Show user')
    user_group.add_argument('--add-user', dest='add_user', action='store',
        help='Add new user')
    user_group.add_argument('--remove-user', dest='remove_user', action='store',
        help='Remove a user')
    user_group.add_argument('--realname', dest='user_realname', action='store',
        default=_d_realname, help='Realname for user')
    user_group.add_argument('--password', dest='user_password', action='store',
        help='Password for new user. If not specified, read from stdin')

    server_group = parser.add_argument_group('servers')
    server_group.add_argument('--add-server', dest='add_server', action='store',
        default=_d_add_server, help='Add a new server')
    server_group.add_argument('--remove-server', dest='remove_server', action='store',
        default=_d_remove_server, help='Remove a server')
    server_group.add_argument('--list-server', dest='list_server', action='store',
        default=_d_list_server, help='Get details for a server')
    server_group.add_argument('--list-servers', dest='list_servers', action='store_true',
        default=_d_list_servers, help='List all servers')
    server_group.add_argument('--owner', dest='owner', action='store',
        default=_d_owner, help='Select owner for new server')
    server_group.add_argument('--protocols', dest='protocols', action='store',
        default=_d_protocols, help='List of protocols used by this server')

    args = parser.parse_args()

    logger = logging.getLogger('main')
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)

    console_logger = logging.StreamHandler()
    console_logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)

    logger.debug('logging at %s' % ll2str[log_level])

    api = API(logger, args.host, args.port)
    if api.ping():
        logger.debug('Connected to API at %s:%s' % (args.host, args.port))
    else:
        logger.error('Failed to connect to API at %s:%s' % (args.host, args.port))
        return

    if args.list_users:
        users = api.get_users()
        if users:
            print "==> Available users:"
            for user in users:
                print("* %s" % user)
        else:
            logger.error('No users configured')
    elif args.add_user:
        users = api.get_users()
        if users and args.add_user in users:
            logger.error('User %s already exists' % args.add_user)
            return
        if args.user_password:
            password = args.user_password
        else:
            password = getpass.getpass('Enter password: ')
        if args.user_realname:
            realname = args.user_realname
        else:
            realname = args.add_user
        user = {
            'username': args.add_user,
            'password': hashlib.sha512(password).hexdigest(),
            'realname': realname

        }
        if api.add_user(user):
            logger.debug('User %s added' % (args.add_user))
        else:
            logger.error('Failed to add user %s' % (args.add_user))
    elif args.list_user:
        user = api.get_user(args.list_user)
        if user:
            print("%s\t%s" % (user['username'], user['realname']))
        else:
            logger.error('User %s not found' % args.list_user)
    elif args.remove_user:
        users =  api.get_users()
        if users and args.remove_user in users:
            api.remove_user(args.remove_user)
            logger.info('User %s removed' % args.remove_user)
        else:
            logger.error('User %s does not exist' % args.remove_user)
    elif args.add_server:
        if not args.owner:
            logger.error('--add-server needs --owner')
            return
        if not args.protocols:
            logger.error('--add-server needs --protocols')
            return
        if isinstance(args.protocols, str):
            args.protocols = args.protocols.split(',')
        server = {
            'servername': args.add_server,
            'owner': args.owner,
            'protocols': args.protocols,
        }
        if api.add_server(server):
            logger.info('Host %s added succesfully for %s' % (args.add_server, args.owner))
        else:
            logger.error('Failed to add %s for %s' % (args.add_server, args.owner))
    elif args.list_servers:
        servers = api.get_servers()
        if servers:
            print('==> Available servers')
            for server in servers:
                print('* %s' % server)
    elif args.remove_server:
        servers = api.get_servers()
        if servers and args.remove_server in servers:
            api.remove_server(args.remove_server)
            logger.info('Server %s removed' % args.remove_server)
        else:
            logger.error('Failed to remove server %s' % args.remove_server)
    elif args.list_server:
        server = api.get_server(args.list_server)
        if server:
            print('Servername: %s' % server['servername'])
            print('Protocols:  %s' % ','.join(server['protocols']))
            print('API token:  %s' % server['apikey'])

    return

if __name__ == '__main__':
    sys.exit(main())
