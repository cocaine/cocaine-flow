# -*- coding: utf-8 -*-
import hashlib
import logging
from uuid import uuid4
import msgpack
from flask import request, render_template, session, flash, redirect, url_for, current_app, json
from pymongo.errors import DuplicateKeyError

log = logging.getLogger()

def logged_in(func):
    def wrapper(*args, **kwargs):
        username = session.get('logged_in')
        if not username:
            return redirect(url_for('login'))

        user = current_app.mongo.db.users.find_one({'_id': session['logged_in']})
        if user is None:
            session.pop('logged_in', None)
            return redirect(url_for('login'))

        return func(user, *args, **kwargs)

    return wrapper


def token_required(func):
    def wrapper(*args, **kwargs):
        token = request.values.get('token')
        if not token:
            return 'Token is required', 403
        user = current_app.mongo.db.users.find_one({'token': token})
        if user is None:
            return 'Valid token is required', 403
        return func(*args, token=token, **kwargs)

    return wrapper


def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


def create_user(username, password, admin=False):
    return current_app.mongo.db.users.insert(
        {'_id': username, 'password': hashlib.sha1(password).hexdigest(), 'admin': admin, 'token': uuid4()},
        safe=True)


def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error="Username/password cannot be empty")

        try:
            create_user(username, password)
        except DuplicateKeyError as e:
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

        session['logged_in'] = user["_id"]
        flash('You were logged in')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@logged_in
def dashboard(user):
    manifests = []
    if user['admin']:
        try:
            manifests = msgpack.unpackb(current_app.elliptics.read('system\0list:manifests'))
        except RuntimeError:
            pass
    return render_template('dashboard.html', user=user, manifests=manifests)


@token_required
def create_profile(name, token=None):
    body = request.json
    if body:
        id = '%s_%s' % (token, name)
        body['_id'] = id
        current_app.mongo.db.profiles.update({'_id': id}, body, upsert=True)

    return ''


def read():
    key = "system\0list:manifests"
    return current_app.elliptics.read_data(key)


@token_required
def upload(branch, revision, token):
    app = request.files.get('app')
    info = request.form.get('info')

    if app is None or info is None:
        return 'Invalid params', 400

    try:
        info = json.loads(info)
    except Exception as e:
        log.exception('Bad encoded json in info parameter')
        return 'Bad encoded json', 400

    package_type = info.get('type')
    if package_type not in ['python']:
        return '%s type is not supported' % package_type, 400

    app_name = info.get('name')
    if app_name is None:
        return 'App name is required in info file', 400

    e = current_app.elliptics

    info['developer'] = token
    info['uuid'] = "%s_%s_%s" % (app_name, branch, revision)
    manifests_key = "system\0list:manifests"

    try:
        e.write("apps\0%s" % info['uuid'], app.read())
        e.write("manifests\0%s" % info['uuid'], msgpack.packb(info))
        manifests = set(msgpack.unpackb(e.read(manifests_key)))
        manifests.add(info['uuid'])
        e.write(manifests_key, msgpack.packb(list(manifests)))
    except Exception:
        return "App storage failure", 500

    return 'ok'
