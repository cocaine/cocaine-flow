# -*- coding: utf-8 -*-
import hashlib
import logging
from flask import request, render_template, session, flash, redirect, url_for, current_app, abort, json
from pymongo.errors import DuplicateKeyError

log = logging.getLogger()

def logged_in(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper


def token_required(func):
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return abort(401)
        return func(*args, token=token, **kwargs)

    return wrapper


def home():
    if 'logged_in' in session:
        return render_template('admin.html')
    return render_template('home.html')


def create_user(username, password, admin=False):
    return current_app.mongo.db.users.insert(
        {'_id': username, 'password': hashlib.sha1(password).hexdigest(), 'admin': admin},
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

        session['logged_in'] = True
        flash('You are registered')

        return redirect(url_for('admin'))
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

        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('admin'))

    return render_template('login.html')


def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@logged_in
def admin():
    return render_template('admin.html')


@token_required
def create_profile(name, token=None):
    body = request.json
    if body:
        id = '%s_%s' % (token, name)
        body['_id'] = id
        current_app.mongo.db.profiles.update({'_id': id}, body, upsert=True)

    return ''


def read():
    key = "system\0list:apps"
    return current_app.elliptics.read_data(key)


def upload():
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

    key = "system\0list:apps"
    blob = current_app.elliptics.write_data(key, app.read())
    return str(blob)
