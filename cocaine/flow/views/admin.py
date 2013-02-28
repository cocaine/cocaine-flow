# -*- coding: utf-8 -*-
from flask import render_template, request
from flask.helpers import json
from cocaine.flow.storages import storage
from views import token_required, logged_in
from cocaine.flow.common import add_prefix


@token_required(admin=True)
def maintenance(user):
    s = storage
    s.clean_manifests()
    s.clean_profiles()
    s.clean_runlists()
    s.clean_hosts()
    return 'ok'


@token_required(admin=True)
def create_host(alias, host, user):
    storage.add_host(alias, host)
    return 'ok'


@token_required(admin=True)
def delete_host(alias, host, user):
    storage.delete_host(alias, host)
    return 'ok'

@token_required(admin=True)
def delete_alias(alias, user):
    storage.delete_alias(alias)
    return 'ok'

@token_required
def create_runlist(name, user):
    try:
        storage.write_runlist(name,{})
    except Exception as err:
        return "Fail"
    else:
        return "ok"

@token_required
def delete_runlist(name, user=None):
    try:
        storage.delete_runlist(name)
    except Exception as err:
        return "Fail"
    else:
        return 'ok'

@token_required
def create_profile(name, user=None):
    body = request.json
    print body
    if body:
        storage.write_profile(name, body)
    return 'ok'

@token_required
def delete_profile(name, user=None):
    storage.delete_profile(name)
    return 'Ok'

def read_balances():
    try:
        balances = storage.read(storage.key('system', "list:balances"))
    except:
        balances = {}

    return balances


@logged_in
def balances(user):
    balances = read_balances()
    return render_template("balances.html", **locals())


@token_required(admin=True)
def add_balance_list(group, app_name, user):
    s = storage
    balances = read_balances()
    try:
        post_body = request.json
    except ValueError:
        return 'Bad encoded JSON body', 400
    print post_body

    if not post_body:
        return 'Empty body', 400

    if not isinstance(post_body, dict):
        return 'Encoded Json dict is required', 400

    for key, int_value in post_body.items():
        try:
            post_body[key] = int(int_value)
        except ValueError:
            return 'Values of dict should be ints', 400

    try:
        s.bulk_read(add_prefix("apps", post_body.keys()))
    except RuntimeError:
        return "One of app's version is not uploaded"

    balances.setdefault(app_name, {})
    balances[app_name]['AppVersions'] = post_body
    balances[app_name]['Cluster'] = group
    print balances
    try:
        s.write(s.key('system', "list:balances"), balances)
    except RuntimeError:
        return 'Failed to save balances to storage', 500

    return 'ok'

@token_required(admin=True)
def remove_balance_list(group, app_name, user):
    pass
