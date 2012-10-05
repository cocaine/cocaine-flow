# -*- coding: utf-8 -*-
from flask import render_template, current_app
from views import token_required, clean_entities, logged_in
from cocaine.flow.common import read_hosts, write_hosts

@token_required(admin=True)
def maintenance(token):
    s = current_app.storage
    clean_entities("manifests", "system", "list:manifests")
    clean_entities("profiles", "system", "list:profiles")
    runlists = clean_entities("runlists", "system", "list:runlists")
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
    return 'ok'


@token_required(admin=True)
def create_host(alias, host, token):
    hosts = read_hosts()
    hosts.setdefault(alias, []).append(host)
    write_hosts(hosts)
    return 'ok'


@token_required(admin=True)
def delete_host(host, token):
    hosts = read_hosts()
    hosts.remove(host)
    write_hosts(hosts)
    return 'ok'


@logged_in
def dealer(user):
    return render_template("dealer.html", user=user)
