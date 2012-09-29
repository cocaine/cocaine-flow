#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _yaml import YAMLError
from time import time
import os
import sys
import yaml
import json
import requests
import cli_settings
from opster import command, dispatch, QuitError
import sh


def upload_packed_app(packed_app_path, package_info, ref, token):
    rv = requests.post(cli_settings.API_SERVER + '/upload',
                       data={
                           'info': json.dumps(package_info),
                           'ref': ref,
                           'token': token
                       },
                       files={'app': open(packed_app_path, 'rb')})
    if rv.status_code != 200:
        raise QuitError('Error during app upload to server. Reason: %s' % rv.text)


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
                raise QuitError(e.stderr)
        else:
            raise QuitError("Unsupported operation with cvs=`%s`" % cvs)

    if cvs == 'git':
        try:
            return sh.git("rev-parse", "--short", ref, _cwd=dir)
        except sh.ErrorReturnCode as e:
            raise QuitError(e.stderr)

    return ref


def get_commit_info(dir, ref):
    cvs = define_cvs(dir)
    return get_real_ref(dir, ref, cvs)


def pack_app(curdir):
    packed_app_path = "/tmp/app.tar.gz"
    try:
        sh.tar("-czf", packed_app_path, "-C", os.path.dirname(curdir), os.path.basename(curdir))
    except sh.ErrorReturnCode as e:
        raise QuitError('Cannot pack application. %s' % str(e))

    return packed_app_path


@command(shortlist=True, usage="[OPTIONS]")
def upload(dir=('d', '.', 'root directory of application'),
           ref=('r', '', 'branch/tag/revision to use'),
           *args, **kwargs):
    '''Upload code to cocaine cloud'''
    cocaine_path = os.path.expanduser("~/.cocaine")
    if not os.path.exists(cocaine_path):
        raise QuitError('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    with open(cocaine_path, 'r') as f:
        secret_key = f.readline()
        if not secret_key:
            raise QuitError('Secret key is not installed. Use `./cocaine-flow token` to do that.')

    curdir = os.path.abspath(dir)
    if not os.path.exists(curdir + '/info.yaml'):
        raise QuitError('info.yaml is required')

    try:
        package_info = yaml.load(file(curdir + '/info.yaml'))
    except YAMLError as e:
        raise QuitError('Bad format of info.yaml')

    real_ref = get_commit_info(curdir, ref)

    if kwargs['verbose']:
        print "Packing application...",
        sys.stdout.flush()

    packed_app_path = pack_app(curdir)

    if kwargs['verbose']:
        print 'Done'
        print 'Uploading application to server...',
        sys.stdout.flush()

    upload_packed_app(packed_app_path, package_info, real_ref, secret_key)

    if kwargs['verbose']:
        print 'Done'
        print "Cleaning...",
        sys.stdout.flush()

    sh.rm("-f", packed_app_path)

    if kwargs['verbose']:
        print 'Done'

    print 'Application is successfully uploaded!'


@command(shortlist=True)
def deploy(runlist, app_uuid, profile_name,
           profile_path=('f', '', 'path to profile file'),
           *args, **kwargs):

    if profile_path:
        profile_path = os.path.abspath(profile_path)
        if not os.path.exists(profile_path) or os.path.isdir(profile_path):
            raise QuitError('Invalid path to profile')

        try:
            profile_info = yaml.load(file(profile_path))
        except YAMLError as e:
            raise QuitError('Bad format of profile yaml')

    url = cli_settings.API_SERVER + '/deploy/%s/%s/%s' % (runlist, app_uuid, profile_name)
    if profile_path:
        rv = requests.post(url, data=json.dumps(profile_info))
    else:
        rv = requests.post(url)

    if rv.status_code != 200:
        raise QuitError('Error during  deploying on server. Reason: %s' % rv.text)

    print 'Done!'


@command(shortlist=True)
def token(secret_key, *args, **kwargs):
    """
    Set secret key
    """
    with open(os.path.expanduser("~/.cocaine"), 'w+') as f:
        f.write(secret_key)
    print "Done!"


options = [('v', 'verbose', False, 'enable additional output'),
           ('q', 'quiet', False, 'suppress output')]

if __name__ == '__main__':
    dispatch(globaloptions=options)
