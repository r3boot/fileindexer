
from __future__ import with_statement

import os

from fabric.api import settings, local

remote_host = 'storage'
remote_dir = '/people/r3boot'

def sync(host=remote_host, directory=remote_dir):
    cwd = os.getcwd()
    with settings(remote_host=host):
        local("rsync -avl --progress --delete --exclude '*.swp' --exclude '*.pyc' %s %s:%s" % (cwd, host, directory))
    

if __name__ == '__main__':
    print('You need to call me through fabric ...')
