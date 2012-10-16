# -*- coding: utf-8 -*-
from flask import render_template, current_app, request
from flask.helpers import json
from cocaine.flow.storages import storage
from views import token_required, clean_entities, logged_in
from cocaine.flow.common import read_hosts, write_hosts, add_prefix


def clean_hosts():
    hosts = storage.read(storage.key('system', "list:hosts"))
    if not isinstance(hosts, dict):
        storage.write(storage.key('system', "list:hosts"), {})


@token_required(admin=True)
def maintenance(user):
    s = storage
    clean_entities("manifests", "system", "list:manifests")
    clean_entities("profiles", "system", "list:profiles")
    runlists = clean_entities("runlists", "system", "list:runlists")

    #clean invalid apps from runlists
    for runlist_name, runlist in runlists.items():
        for app_uuid, profile_name in runlist.items():
            try:
                s.read(s.key("apps", app_uuid))
            except RuntimeError:
                del runlists[runlist_name][app_uuid]

            try:
                s.read(s.key("profiles", profile_name))
            except RuntimeError:
                runlists[runlist_name][app_uuid] = 'default'

    for runlist_name, runlist in runlists.items():
        s.write(s.key("runlists", runlist_name), runlist)

    s.write(s.key("system", "list:runlists"), runlists.keys())

    clean_hosts()

    return 'ok'


@token_required(admin=True)
def create_host(alias, host, user):
    hosts = read_hosts()
    hosts.setdefault(alias, []).append(host)
    write_hosts(hosts)
    return 'ok'


@token_required(admin=True)
def delete_host(host, user):
    hosts = read_hosts()
    hosts.remove(host)
    write_hosts(hosts)
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
