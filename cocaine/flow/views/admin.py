# -*- coding: utf-8 -*-
from views import token_required, clean_entities
from cocaine.flow.common import read_hosts, write_hosts

@token_required(admin=True)
def maintenance(token):
    clean_entities("manifests", "system", "list:manifests")
    clean_entities("runlists", "system", "list:runlists")
    clean_entities("profiles", "system", "list:profiles")
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
