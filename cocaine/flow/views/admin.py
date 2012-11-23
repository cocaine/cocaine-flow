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
        post_body = json.loads(request.stream.read())
    except ValueError:
        return 'Bad encoded JSON body', 400

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

    balances.setdefault(group, {}).setdefault(app_name, {})
    balances[group][app_name] = post_body
    try:
        s.write(s.key('system', "list:balances"), balances)
    except RuntimeError:
        return 'Failed to save balances to storage', 500

    return 'ok'
