# -*- coding: utf-8 -*-
from collections import Iterable
from copy import copy
from yaml import YAMLError
import hashlib
import logging
import os
from uuid import uuid4
from flask import request, render_template, session, flash, redirect, url_for, current_app, json
from pymongo.errors import DuplicateKeyError
import sh
import yaml
from cocaine.flow.storages import storage
from common import send_json_rpc, token_required, uniform, logged_in
from cocaine.flow.common import read_hosts, read_entities, list_add, list_remove, dict_remove


logger = logging.getLogger()


def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


def create_user(username, password, admin=False):
    return current_app.mongo.db.users.insert(
        {'_id': username, 'password': hashlib.sha1(password).hexdigest(), 'admin': admin, 'token': str(uuid4())},
        safe=True)


def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error="Username/password cannot be empty")

        try:
            create_user(username, password)
        except DuplicateKeyError:
            return render_template('register.html', error="Username is not available")

        session['logged_in'] = username
        flash('You are registered')

        return redirect(url_for('dashboard'))
    return render_template('register.html')


def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = current_app.mongo.db.users.find_one({'_id': username})
        if user is None:
            return render_template('login.html', error='Invalid username')

        if user['password'] != hashlib.sha1(password).hexdigest():
            return render_template('login.html', error='Invalid password')

        token = user.get('token')
        if not token:
            return render_template('login.html', error='User doesn\'t have token')

        session['logged_in'] = token
        flash('You were logged in')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@logged_in
def dashboard(user):
    try:
        manifests = read_entities("manifests", "system", "list:manifests")
        grouped_manifests = {}
        for uuid, manifest in manifests.items():
            if not user['admin'] and user['token'] != manifest['developer']:
                continue

            common_manifest_part = grouped_manifests.setdefault(manifest['name'], {})
            common_manifest_part.setdefault('description', manifest['description'])
            common_manifest_part.setdefault('type', manifest['type'])
            common_manifest_part.setdefault('manifests', []).append(manifest)

    except RuntimeError as e:
        logger.warning(str(e))
        manifests = {}

    try:
        runlists = read_entities("runlists", "system", "list:runlists")
    except RuntimeError as e:
        logger.warning(str(e))
        runlists = {}

    try:
        profiles = read_entities("profiles", "system", "list:profiles")
    except RuntimeError as e:
        logger.warning(str(e))
        profiles = {}

    return render_template('dashboard.html', hosts=read_hosts(), **locals())


@logged_in
def dashboard_edit(user):
    value = request.form.get('value')
    id = request.form.get('id')
    if not id:
        return value

    split_id = id.split(':')
    entity_type = split_id[0]
    if entity_type == 'profile':
        profile_name = split_id[1]
        option = split_id[2]
        profile_key = storage.key("profiles", profile_name)
        profile = storage.read(profile_key)
        if option in profile:
            profile[option] = value
            storage.write(profile_key, profile)
        else:
            return split_id[3] # old value

    return value

@logged_in
def stats(user):
    hosts = read_hosts()
    if not hosts:
        return render_template('stats.html', user=user, hosts={})

    hosts = send_json_rpc({'version': 2, 'action': 'info'}, set(*[host for host in hosts.values()]))
    return render_template('stats.html', user=user, hosts=hosts)


def process_json_rpc_response(res, uuid):
    for host, rv in res.items():
        answer = rv[uuid]
        error = answer.get('error')
        if error:
            return error, 500
    else:
        return 'ok'


def start_app(uuid, profile):
    res = send_json_rpc({'version': 2, 'action': 'create', 'apps': {uuid: profile}}, read_hosts())
    return process_json_rpc_response(res, uuid)


def stop_app(uuid):
    res = send_json_rpc({'version': 2, 'action': 'delete', 'apps': [uuid]}, read_hosts())
    return process_json_rpc_response(res, uuid)


@token_required
def create_profile(name, user=None):
    body = request.json
    if body:
        id = '%s_%s' % (user.token, name)
        body['_id'] = id
        current_app.mongo.db.profiles.update({'_id': id}, body, upsert=True)

    return ''


def exists(prefix, postfix):
    try:
        return str(storage.read(storage.key(prefix, postfix)))
    except:
        return 'Not exists', 404


def validate_info(info):
    package_type = info.get('type')
    if package_type not in ['python']:
        raise ValueError('%s type is not supported' % package_type)

    app_name = info.get('name')
    if app_name is None:
        raise KeyError('App name is required in info file')

    if info.get('description') is None:
        raise KeyError('App description is required in info file')


def upload_app(app, info, ref, token):
    validate_info(info)

    ref = ref.strip()
    info['uuid'] = ("%s_%s" % (info['name'], ref)).strip()
    info['developer'] = token

    s = storage

    # app
    app_key = storage.key("apps", info['uuid'])
    logger.info("Writing app to `%s`" % app_key)
    s.write(app_key, app.read())

    #manifests
    manifest_key = storage.key("manifests", info['uuid'])
    info['ref'] = ref
    logger.info("Writing manifest to `%s`" % manifest_key)
    s.write(manifest_key, info)

    list_add("system", "list:manifests", info['uuid'])

    return info['uuid']


def download_depends(depends, type_, path):
    if type_ == 'python':
        install_path = "%s/depends" % path
        #        pip install -b /tmp  --src=/tmp --install-option="--install-lib=/home/inkvi/test" -v msgpack-python
        output = sh.pip("install", "-v", "-I", "-b", path, "--src", path, "--install-option",
                        "--install-lib=%s" % install_path, *depends)
        return os.listdir(install_path)


def upload_repo(token):
    url = request.form.get('url')
    type_ = request.form.get('type')
    ref = request.form.get('ref')

    if not url or not type_:
        return 'Empty type or url', 400
    if type_ not in ['git', 'cvs', 'hg']:
        return 'Invalid cvs type', 400

    clone_path = "/tmp/%s" % os.path.basename(url)
    if os.path.exists(clone_path):
        sh.rm("-rf", clone_path)

    if type_ == 'git':
        ref = ref or "HEAD"
        sh.git("clone", url, clone_path)

        try:
            ref = sh.git("rev-parse", ref, _cwd=clone_path).strip()
        except sh.ErrorReturnCode as e:
            return 'Invalid reference. %s' % e, 400

        if not os.path.exists(clone_path + "/info.yaml"):
            return 'info.yaml is required', 400

        try:
            package_info = yaml.load(file(clone_path + '/info.yaml'))
            validate_info(package_info)
        except YAMLError:
            return 'Bad encoded info.yaml', 400
        except (ValueError, KeyError) as e:
            return str(e), 400

        try:
            depends_path = download_depends(package_info['depends'], package_info['type'], clone_path)
        except sh.ErrorReturnCode as e:
            return 'Unable to install dependencies. %s' % e, 503

        # remove info.yaml from tar.gz
        with open(clone_path + '/.gitattributes', 'w') as f:
            f.write('info.yaml export-ignore')

        try:
            sh.git("archive", ref, "--worktree-attributes", format="tar", o="app.tar", _cwd=clone_path),
            sh.tar("-uf", "app.tar", "-C", clone_path + "/depends", *depends_path, _cwd=clone_path)
            sh.gzip("app.tar", _cwd=clone_path)
        except sh.ErrorReturnCode as e:
            return 'Unable to pack application. %s' % e, 503

        try:
            with open(clone_path + "/app.tar.gz") as app:
                uuid = upload_app(app, package_info, ref, token)
            return "Application %s was successfully uploaded" % uuid
        except (KeyError, ValueError) as e:
            return str(e), 400

    return "Application was failed to upload", 400


@token_required
def upload(user):
    if request.method == 'GET':
        return render_template('upload.html', user=user)

    url = request.form.get('url')
    if url:
        return upload_repo(user['token'])

    app = request.files.get('app')
    info = request.form.get('info')
    ref = request.form.get('ref')

    if app is None or info is None or ref is None:
        return 'Invalid params', 400

    try:
        package_info = json.loads(info)
    except Exception as e:
        logger.exception('Bad encoded json in info parameter')
        return 'Bad encoded json', 400

    try:
        uuid = upload_app(app, package_info, ref, user['token'])
    except (KeyError, ValueError) as e:
        return str(e), 400

    return 'Application %s was successfully uploaded' % uuid


@token_required(admin=True)
def deploy(runlist, uuid, profile, user):
    s = storage

    #read manifest
    manifest_key = s.key('manifests', uuid)
    try:
        manifest = s.read(manifest_key)
    except RuntimeError:
        return 'Manifest for app doesn\'t exists', 400


    # read runlists
    runlist_key = s.key("runlists", runlist)
    logger.info('Reading %s', runlist_key)
    try:
        runlist_dict = s.read(runlist_key)
    except RuntimeError:
        runlist_dict = {}

    hosts = read_hosts()
    if not hosts:
        return 'No hosts are available', 400

    post_body = request.stream.read()
    if post_body:
        s.write(s.key('profiles', profile), json.loads(post_body))
        list_add("system", "list:profiles", profile)
    else:
        try:
            s.read(s.key('profiles', profile))
        except RuntimeError:
            return 'Profile name is not valid'

    # update runlists
    runlist_dict[uuid] = profile
    logger.info('Writing runlist %s', runlist_key)
    s.write(runlist_key, runlist_dict)

    #manifest update
    manifest['runlist'] = runlist
    s.write(manifest_key, manifest)

    list_add("system", "list:runlists", runlist)
    res = send_json_rpc({'version': 2, 'action': 'create', 'apps': {uuid: profile}}, *hosts.values())
    for host, host_res in res.items():
        for app_uuid, res in host_res.items():
            if 'error' in res:
                return "%s - %s" % (app_uuid, res['error']), 500
            logger.debug("Deploy: %s. %s", app_uuid, res)

    return 'ok'


def delete_app(app_name):
    s = storage

    # define runlist for app from manifest
    runlist = storage.read(s.key('manifests', app_name)).get('runlist')
    logger.info("Runlist in manifest is %s", runlist)
    if runlist is not None:
        logger.warning('Trying to delete deployed app')
        return 'error', 400

    list_remove("system", "list:manifests", app_name)

    s.remove(s.key('manifests', app_name))
    s.remove(s.key('apps', app_name))

    return 'ok'


def get_hosts():
    return json.dumps(read_hosts())


def clean_entities(prefix, list_prefix, list_postfix, except_='default'):
    s = storage
    rv = {}
    entities_keys = s.read(s.key(list_prefix, list_postfix))
    if not isinstance(entities_keys, Iterable):
        s.write(s.key(list_prefix, list_postfix), list())
        return

    original_keys = set(entities_keys)
    cleaned_keys = copy(original_keys)
    for key in original_keys:
        try:
            rv[key] = s.read(s.key(prefix, key))
        except RuntimeError:
            if key != except_:
                cleaned_keys.remove(key)
    keys_for_remove = original_keys - cleaned_keys
    if keys_for_remove:
        s.write(s.key(list_prefix, list_postfix), list(cleaned_keys))
        logger.info('Removed %s during maintenance %s', prefix, keys_for_remove)

    return rv


def get_token():
    username = request.form.get('username')
    password = request.form.get('password')
    user = current_app.mongo.db.users.find_one({'_id': username})
    if user is None:
        return 'Username is invalid', 400

    if user['password'] != hashlib.sha1(password).hexdigest():
        return 'Password is invalid', 400

    token = user.get('token')
    if token is None:
        return 'Token is not set for user', 400
    return str(token)


def error_handler(exc):
    logger.error(exc)
    if isinstance(exc, RuntimeError):
        return 'Storage failure', 500
    raise exc
