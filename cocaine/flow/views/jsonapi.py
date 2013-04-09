import hashlib

from flask import request, render_template, session, flash, redirect, url_for, current_app, json, jsonify

from common import send_json_rpc, token_required, token_required_json, uniform, logged_in, logged_in_json
from storages.exceptions import UserExists
from cocaine.flow.storages import storage
from .views import create_user, is_valid_username, is_valid_password

# JSON API
def get_apps():
    try:
        mm = storage.read_manifests()
        return json.dumps([k for k in mm.iterkeys()])
    except RuntimeError:
        return jsonify([])

def get_hosts():
    return json.dumps(storage.read_hosts())

def get_runlists():
    try:
        return json.dumps(storage.read(storage.key("system", "list:runlists")))
    except RuntimeError:
        return json.dumps([])

def get_runlists_apps():
    return json.dumps(storage.read_runlists())
# 

def auth():
    username = request.values.get('username')
    password = request.values.get('password')
    user = storage.find_user_by_username(username)
    if user is None:
        return jsonify({"reason" :'Username is invalid', "result" : "fail"})

    if user['password'] != hashlib.sha1(password).hexdigest():
        return jsonify({"reason" :'Password is invalid', "result" : "fail"})

    token = user.get('token')
    if token is None:
        return jsonify({"reason" : 'Token is not set for user', "result" : "fail"})
    session['logged_in'] = token
    return jsonify({"result" : "ok", "token":token, "login" : username, "ACL" : {}})

def check_login():
    username = request.values.get("login")
    user = storage.find_user_by_username(username)
    if user is not None:
        return jsonify({"result" : "ok"})
    else:
        return jsonify({"result" : "fail"})

@token_required_json(admin=False)
def userinfo(user):
    print user
    return jsonify({"result" : "ok", "ACL" : {}, "login" : storage.get_username_by_token(user.get('token'))})


def register_json():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username is None or not is_valid_username(username):
            return jsonify({"error" :'Username is incorrect', "result" : "fail", "code" : 2})
        if password is None or not is_valid_password(password):
            return jsonify({"error" :'Password is incorrect', "result" : "fail", "code" : 3})
        try:
            create_user(username, password)
        except UserExists:
            return jsonify({"error" :'User exists', "result" : "fail", "code" : 1 })
        try:
            user = storage.find_user_by_username(username)
        except Exception:
            return jsonify({"result" : "fail", "error" : "Unknown register error", "code" : -1})
        res = { "result" : "ok", "login" : username }
        user.pop("password")
        res.update(user)
        return jsonify(res)

@logged_in_json
def logout_json(user):
    session.pop("logged_in", None)
    return jsonify({"result" : "ok"})
