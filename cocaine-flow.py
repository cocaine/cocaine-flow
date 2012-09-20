#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from time import time
import os
import sys
import yaml
import json
import requests
import settings
from opster import command, dispatch


def upload_packed_app(packed_app_path, package_info, branch, rev):
    rv = requests.post(settings.API_SERVER + '/upload/%s/%s' % (branch, rev),
                       data={'info': json.dumps(package_info),
                             'token': '123'},
                       files={'app': open(packed_app_path, 'rb')})
    if rv.status_code != 200:
        raise command.Error('Error during app upload to server. Reason: %s' % rv.text)


def define_cvs(dir):
    if os.path.exists(dir + '/.git'):
        return 'git'
    if os.path.exists(dir + '/.svn'):
        return 'svn'
    return 'fs'


def get_real_branch(branch, cvs):
    if cvs == 'fs':
        return 'local'
    if cvs == 'git':
        return subprocess.call("git branch | grep \* | awk '{print $2}'")

    sys.exit(1)


def get_real_revision(rev, cvs):
    if cvs == 'fs':
        return int(time())


def get_commit_info(dir, branch, rev):
    cvs = define_cvs(dir)
    return get_real_branch(branch, cvs), get_real_revision(rev, cvs)


@command(shortlist=True)
def upload(branch=('b', None, 'branch to use'),
           rev=('r', None, 'revision to use'),
           dir=('d', '.', 'root directory of application')):
    '''Upload code to cocaine cloud'''

    if not os.path.exists(os.path.expanduser("~/.cocaine")):
        raise command.Error('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    with open(os.path.expanduser("~/.cocaine"), 'r') as f:
        if not f.readline():
            raise command.Error('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    curdir = os.path.abspath(dir)
    if not os.path.exists(curdir + '/info.yaml'):
        raise command.Error('info.yaml is required')

    package_info = yaml.load(file(curdir + '/info.yaml'))
    package_type = package_info.get('type')
    if package_type is None:
        raise command.Error('type is not set in info.yaml')

    packed_app_path = "%s/app.tar.gz" % curdir
    cmd = 'tar czf %s * -C %s' % (packed_app_path, curdir)
    try:
        subprocess.call(cmd, shell=True)
    except (subprocess.CalledProcessError, OSError):
        raise command.Error('Cannot pack application. Command: %s' % cmd)

    real_branch, real_revision = get_commit_info(curdir, branch, rev)
    upload_packed_app(packed_app_path, package_info, real_branch, real_revision)
    subprocess.call("rm %s" % packed_app_path, shell=True)
    print package_info


@command(shortlist=True)
def token(secret_key):
    """
    Set secret key
    """
    with open(os.path.expanduser("~/.cocaine"), 'r+') as f:
        f.write(secret_key)


if __name__ == '__main__':
    dispatch()
