#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
import os
import yaml
import json
import requests
import settings
from opster import command, dispatch
import sh


def upload_packed_app(packed_app_path, package_info, ref, token):
    rv = requests.post(settings.API_SERVER + '/upload/%s' % ref,
                       data={'info': json.dumps(package_info),
                             'token': token},
                       files={'app': open(packed_app_path, 'rb')})
    if rv.status_code != 200:
        raise command.Error('Error during app upload to server. Reason: %s' % rv.text)


def define_cvs(dir):
    if os.path.exists(dir + '/.git'):
        return 'git'
    if os.path.exists(dir + '/.svn'):
        return 'svn'
    if os.path.exists(dir + '/.hg'):
        return 'hg'
    return 'fs'


def get_real_ref(dir, ref, cvs):
    if cvs == 'fs':
        return int(time())

    if not ref:
        if cvs == 'git':
            try:
                return sh.git("rev-parse", "HEAD", _cwd=dir)
            except sh.ErrorReturnCode as e:
                raise command.Error(e.stderr)
        else:
            raise command.Error("Unsupported operation with cvs=`%s`" % cvs)

    if cvs == 'git':
        try:
            return sh.git("rev-parse", "--short", ref, _cwd=dir)
        except sh.ErrorReturnCode as e:
            raise command.Error(e.stderr)

    return ref


def get_commit_info(dir, ref):
    cvs = define_cvs(dir)
    return get_real_ref(dir, ref, cvs)


def pack_app(curdir, real_ref):
    packed_app_path = "/tmp/app.tar.gz"
    try:
        sh.tar("-czf", packed_app_path, "-C", os.path.dirname(curdir), os.path.basename(curdir))
    except sh.ErrorReturnCode as e:
        raise command.Error('Cannot pack application. %s' % str(e))

    return packed_app_path


@command(shortlist=True, usage="[OPTIONS]")
def upload(dir=('d', '.', 'root directory of application'),
           ref=('r', '', 'branch/tag/revision to use'),
           *args, **kwargs):
    '''Upload code to cocaine cloud'''
    cocaine_path = os.path.expanduser("~/.cocaine")
    if not os.path.exists(cocaine_path):
        raise command.Error('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    with open(cocaine_path, 'r') as f:
        secret_key = f.readline()
        if not secret_key:
            raise command.Error('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    curdir = os.path.abspath(dir)
    if not os.path.exists(curdir + '/info.yaml'):
        raise command.Error('info.yaml is required')

    package_info = yaml.load(file(curdir + '/info.yaml'))
    package_type = package_info.get('type')
    if package_type is None:
        raise command.Error('type is not set in info.yaml')

    real_ref = get_commit_info(curdir, ref)

    packed_app_path = pack_app(curdir, real_ref)
    if kwargs['verbose']:
        print 'App is packed'

    upload_packed_app(packed_app_path, package_info, real_ref, secret_key)
    if kwargs['verbose']:
        print 'App is uploaded'

    sh.rm("-f", packed_app_path)

    if kwargs['verbose']:
        print 'Done'


@command(shortlist=True)
def token(secret_key):
    """
    Set secret key
    """
    with open(os.path.expanduser("~/.cocaine"), 'w+') as f:
        f.write(secret_key)


options = [('v', 'verbose', False, 'enable additional output'),
           ('q', 'quiet', False, 'suppress output')]

if __name__ == '__main__':
    dispatch(globaloptions=options)
