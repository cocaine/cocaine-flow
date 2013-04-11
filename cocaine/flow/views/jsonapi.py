import hashlib
import time

from flask import json
from flask import jsonify
from flask import request
from flask import redirect
from flask import stream_with_context
from flask import session
from flask import Response

from common import token_required_json
from common import logged_in
from common import logged_in_json

from storages.exceptions import UserExists
from cocaine.flow.storages import storage
from .views import create_user
from .views import is_valid_username
from .views import is_valid_password


def streamed_response():
    @stream_with_context
    def generate():
        yield "Hello\n"
        time.sleep(1)
        yield "Hello\n"
    return Response(generate())

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

def check_username():
    username = request.values.get("username")
    user = storage.find_user_by_username(username)
    if user is not None:
        return jsonify({"result" : "fail"})
    else:
        return jsonify({"result" : "ok"})

@token_required_json(admin=False)
def userinfo(user):
    print "userinfo", user
    return jsonify({"result" : "ok", "ACL" : {}, "login" : storage.get_username_by_token(user.get('token'))})

@token_required_json(admin=True)
def user_remove(user):
    username = request.values.get("username")
    if username is None:
        return jsonify({"result" : "fail", "error" : "no username"})

    try:
        print username
        removing_user = storage.find_user_by_username(username)
    except Exception:
        return jsonify({"result" : "fail", "error" : "Unknown error", "code" : -1})
    if removing_user is not None:
        print removing_user
        return jsonify({"A" : "OK"})
    else:
        return jsonify({"result" : "fail", "error" : "Wrong user name", "code" : -1})




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
        token = user.get('token')
        if token is None:
            return jsonify({"reason" : 'Token is not set for user', "result" : "fail"})
        session['logged_in'] = token
        return jsonify({"result" : "ok", "token":token, "login" : username, "ACL" : {}})
        #res = { "result" : "ok", "login" : username }
        #user.pop("password")
        #res.update(user)
        #return jsonify(res)

@logged_in_json
def logout_json(user):
    session.pop("logged_in", None)
    return jsonify({"result" : "ok"})
