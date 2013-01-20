# -*- coding: utf-8 -*-
from collections import Iterable
from copy import copy
import re
from yaml import YAMLError
import hashlib
import logging
import os
from uuid import uuid4
from flask import request, render_template, session, flash, redirect, url_for, current_app, json, jsonify
import sh
import yaml
from cocaine.flow.storages import storage
from common import send_json_rpc, token_required, uniform, logged_in
from .profile import PROFILE_OPTION_VALIDATORS
from storages.exceptions import UserExists


logger = logging.getLogger()


def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


def create_user(username, password, admin=False):
    token = str(uuid4())
    password = hashlib.sha1(password).hexdigest()
    return storage.create_user(username, password, admin, token)


def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error="Username/password cannot be empty")

        try:
            create_user(username, password)
        except UserExists:
            return render_template('register.html', error="Username is not available")

        session['logged_in'] = username
        flash('You are registered')

        return redirect(url_for('dashboard'))
    return render_template('register.html')


def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = storage.find_user_by_username(username)
        if user is None:
            return render_template('login.html', error='Invalid username')

        if user['password'] != hashlib.sha1(password).hexdigest():
            return render_template('login.html', error='Invalid password')

        token = user.get('token')
        if not token:
            return render_template('login.html', error='User doesn\'t have token')

        session['logged_in'] = token
        return redirect(url_for('dashboard'))

    return render_template('login.html')


def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@logged_in
def dashboard(user):
    grouped_manifests = {}

    manifests = storage.read_manifests()
    for uuid, manifest in manifests.items():
        if not user['admin'] and user['token'] != manifest['developer']:
            continue

        #manifest['git_to_html_url'] = None 
        if manifest.get('url') is not None:
            try:
                manifest['git_to_html_url'] = "http"+''.join(manifest['url'][3:]) 
            except Exception as err:
                print str(err)
        manifest['developer_username'] = storage.get_username_by_token(manifest['developer'])
        common_manifest_part = grouped_manifests.setdefault(manifest['name'], {})
        common_manifest_part.setdefault('description', manifest['description'])
        common_manifest_part.setdefault('type', manifest['type'])
        common_manifest_part.setdefault('manifests', []).append(manifest)
    runlists = storage.read_runlists()
    profiles = storage.read_profiles()
    return render_template('dashboard.html', hosts=storage.read_hosts(), **locals())


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
        profile = storage.read_profile(profile_name)
        if option in profile:
            validator = PROFILE_OPTION_VALIDATORS.get(option)
            if validator:
                try:
                    validator(value)
                except Exception:
                    logging.exception('invalid value %s for `%s` profile option' % (value, option))
                    return split_id[3]
            profile[option] = value
            storage.write_profile(profile_name, profile)
        else:
            return split_id[3] # old value

    return value

@logged_in
def stats(user):
    hosts = storage.read_hosts()
    if not hosts:
        return render_template('stats.html', user=user, hosts={})

    hosts = send_json_rpc(2, [], set(*[host for host in hosts.values()]))
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
    res = send_json_rpc(0, [{uuid: profile}], storage.read_hosts())
    return process_json_rpc_response(res, uuid)


def stop_app(uuid):
    res = send_json_rpc(1, [[uuid]], storage.read_hosts())
    return process_json_rpc_response(res, uuid)


def get_profiles():
    profiles = storage.read_profiles()
    view = request.values.get('view')
    if view == 'dict':
        return jsonify(dict([(profile, profile) for profile in profiles.keys()]))
    return json.dumps(profiles.keys())


@token_required
def create_profile(name, user=None):
    body = request.json
    if body:
        storage.write_profile(name, body)
    return 'ok'


def exists(prefix, postfix):
    try:
        return str(storage.read(storage.key(prefix, postfix)))
    except:
        return 'Not exists', 404


def validate_info(info):
    logger.debug('Validating package info')
    package_type = info.get('type')
    if package_type not in ['python']:
        raise ValueError('%s type is not supported' % package_type)

    app_name = info.get('name')
    if app_name is None:
        raise KeyError('App name is required in info file')

    if info.get('description') is None:
        raise KeyError('App description is required in info file')


def upload_app(app, info, ref, token):
    logger.debug('Uploading application')

    validate_info(info)

    app_name = request.values.get('name')
    if app_name:
        info['uuid'] = app_name.strip()
    else:
        ref = ref.strip()
        info['uuid'] = ("%s_%s" % (info['name'], ref)).strip()

    info['developer'] = token

    s = storage

    # app
    s.save_app(info['uuid'], app)

    #manifests
    info['ref'] = ref
    s.write_manifest(info['uuid'], info)

    return info['uuid']


def download_depends(depends, type_, path):
    logger.debug('Downloading dependencies for %s', path)
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

    if not url:
        return 'Empty url', 400

    if not type_:
        if url.startswith('git://') or url.endswith('.git'):
            type_ = 'git'
        else:
            return 'Cannot define type of repository by url. Please, specify type.', 400

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
            logger.debug("Packing application to tar.gz")
            sh.git("archive", ref, "--worktree-attributes", format="tar", o="app.tar", _cwd=clone_path),
            sh.tar("-uf", "app.tar", "-C", clone_path + "/depends", *depends_path, _cwd=clone_path)
            sh.gzip("app.tar", _cwd=clone_path)
            package_files = sh.tar('-tf', 'app.tar.gz', _cwd=clone_path)
            package_info['structure'] = [f.strip() for f in package_files]
        except sh.ErrorReturnCode as e:
            return 'Unable to pack application. %s' % e, 503

        try:
            for line in sh.git("log", "-5", date="short", format="%h %ad %s [%an]", _cwd=clone_path):
                line = line.strip()

                # git log output is using ansi terminal codes which is messy for our purposes
                ansisequence = re.compile(r'\x1B\[[^A-Za-z]*[A-Za-z]')
                line = ansisequence.sub('', line)
                line = line.strip("\x1b=\r")
                line = line.strip("\x1b>")
                if not line:
                    continue
                package_info.setdefault('changelog', []).append(line)
        except sh.ErrorReturnCode as e:
            return 'Unable to pack application. %s' % e, 503


        try:
            with open(clone_path + "/app.tar.gz") as app:
                package_info['url'] = url
                uuid = upload_app(app, package_info, ref, token)
            return "Application %s was successfully uploaded" % uuid
        except (KeyError, ValueError) as e:
            return str(e), 400

    return "Application was failed to upload", 400

@uniform
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
    except Exception:
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

    is_undeploy = (request.endpoint == 'undeploy')

    #read manifest
    manifest = s.read_manifest(uuid)
    if manifest is None:
        return 'Manifest for app %s doesn\'t exists' % uuid, 400

    # read runlists
    runlist_dict = s.read_runlist(runlist, {})

    hosts = s.read_hosts()
    if not hosts:
        return 'No hosts are available', 400

    post_body = request.stream.read()
    if post_body and not is_undeploy:
        s.write_profile(profile, json.loads(post_body))
    else:
        if s.read_profile(profile) is None:
            return 'Profile name is not valid', 400

    # update runlists
    if is_undeploy:
        if uuid not in runlist_dict:
            return '%s app is not deployed' % uuid, 400
        del runlist_dict[uuid]
    else:
        runlist_dict[uuid] = profile

    #manifest update
    if is_undeploy:
        manifest.pop('runlist', None)
    else:
        manifest['runlist'] = runlist

    if is_undeploy:
        res = send_json_rpc(1, [[uuid]], *hosts.values())
    else:
        res = send_json_rpc(0, [{uuid: profile}], *hosts.values())

    logger.debug("JSON RPC Response: %s" % res)
    for host, host_res in res.items():
        if not host_res:
            return 'Cocaine RPC on %s didn\'t process call' % host, 500
        for app_uuid, res in host_res.items():
            if 'error' in res:
                return "%s - %s" % (app_uuid, res['error']), 500
            logger.debug("Deploy: %s. %s", app_uuid, res)

    s.write_runlist(runlist, runlist_dict)
    s.write_manifest(uuid, manifest)

    return 'ok'


def delete_app(app_name):
    s = storage

    # define runlist for app from manifest
    runlist = storage.read_manifest(app_name, default={}).get('runlist')
    logger.info("Runlist in manifest is %s", runlist)
    if runlist is not None:
        logger.warning('Trying to delete deployed app - rejected')
        return 'error', 400

    storage.remove_app(app_name)
    return 'ok'


def get_hosts():
    return json.dumps(storage.read_hosts())


def get_token():
    username = request.form.get('username')
    password = request.form.get('password')
    user = storage.find_user_by_username(username)
    if user is None:
        return 'Username is invalid', 400

    if user['password'] != hashlib.sha1(password).hexdigest():
        return 'Password is invalid', 400

    token = user.get('token')
    if token is None:
        return 'Token is not set for user', 400
    return str(token)


def get_runlists():
    try:
        return json.dumps(storage.read(storage.key("system", "list:runlists")))
    except RuntimeError:
        return json.dumps([])


def error_handler(exc):
    logger.error(exc)
    if isinstance(exc, RuntimeError):
        return 'Storage failure', 500
    raise exc
