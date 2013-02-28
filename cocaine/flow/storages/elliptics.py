# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import Iterable
from copy import copy
import logging
import msgpack
from .storage import Storage
from elliptics import Logger, Node
import traceback
from storages.exceptions import UserExists


logger = logging.getLogger('storages.elliptics')


class Elliptics(Storage):
    def __init__(self, nodes, groups):
        self.node = Node(Logger("/tmp/cocainoom-elliptics.log"))
        for host, port in nodes.iteritems():
            try:
                self.node.add_remote(host, int(port))
            except RuntimeError:
                # already connected to the host
                traceback.print_exc()

        try:
            from elliptics import Session

            self.storage = Session(self.node)
        except ImportError:
            self.storage = self.node

        self.storage.add_groups(groups)

    def key(self, key, *args):
        prefix = key
        postfix = args[0]

        if type(postfix) in set([tuple, list, set]):
            return type(postfix)(["%s\0%s" % (prefix, p) for p in postfix])

        return "%s\0%s" % (prefix, postfix)

    def create_user(self, username, hashed_password, admin, token):
        try:
            self.read(self.key('users', username))
            raise UserExists
        except RuntimeError:
            self.write(self.key('users', username), {'password': hashed_password, 'admin': admin, 'token': token})
            self.write(self.key('tokens', token), username)

    def remove_prefix(self, prefix, key):
        prefix = "%s\0" % prefix
        if isinstance(key, dict):
            return dict((k.replace(prefix, ''), v) for k, v in key.items())

        return key.replace(prefix, '')

    #========================================================================================
    """
      Operations with Entities:
        read_entities
        write_entity
        delete_entity
    """

    def read_entities(self, prefix, list_prefix, list_postfix):
        s = self
        entities = s.bulk_read(s.key(prefix, s.read(s.key(list_prefix, list_postfix))))
        entities = self.remove_prefix(prefix, entities)
        for k, entity in entities.items():
            entity_unpacked = msgpack.unpackb(entity, list_hook=list)
            entities[k] = entity_unpacked
        return entities

    def write_entity(self, prefix, postfix, list_prefix, list_postfix, data):
        self.write(self.key(prefix, postfix), data)
        self.list_add(list_prefix, list_postfix, postfix)

    def delete_entity(self, prefix, postfix, list_prefix, list_postfix):
        """
            Delete entity item like one runlist of profile
        """
        self.remove(self.key(prefix, postfix))
        self.list_remove(list_prefix, list_postfix, postfix)

    def clean_entities(self, prefix, list_prefix, list_postfix, except_='default'):
        """
            Remove invalid items from entity list
        """
        s = self
        rv = {}
        entities_keys = s.read(s.key(list_prefix, list_postfix))
        if not isinstance(entities_keys, Iterable):
            s.write(s.key(list_prefix, list_postfix), list())
            return

        original_keys = set(entities_keys)
        cleaned_keys = copy(original_keys)
        for key in original_keys:
            try:
                rv[key] = s.read(s.key(prefix, key))
            except RuntimeError:
                if key != except_:
                    cleaned_keys.remove(key)
        keys_for_remove = original_keys - cleaned_keys
        if keys_for_remove:
            s.write(s.key(list_prefix, list_postfix), list(cleaned_keys))
            logger.info('Removed %s during maintenance %s', prefix, keys_for_remove)

        return rv
    #=======================================================================================
    """
        Operations with List
    """

    def list_add(self, prefix, postfix, value, raise_on_missed_key=False):
        storage_key = self.key(prefix, postfix)
        try:
            logger.info("Reading from elliptics %s", storage_key)
            entities = set(self.read(storage_key))
        except RuntimeError:
            if raise_on_missed_key: raise
            entities = set()

        if value not in entities:
            entities.add(value)
            logger.info("Adding `%s` to list of entities by key %s" % (value, prefix + postfix))
            self.write(storage_key, list(entities))

    def list_remove(self, prefix, postfix, value):

        list_key = self.key(prefix, postfix)
        entities = set(self.read(list_key))

        if value in entities:
            entities.remove(value)

            # removing manifest from manifest list
            self.write(list_key, list(entities))

    #======================================================================================
    """
        Manifest
    """

    def read_manifests(self):
        return self.read_entities("manifests", "system", "list:manifests")

    def read_manifest(self, uuid, default=None):
        try:
            return self.read(self.key('manifests', uuid))
        except RuntimeError:
            return default

    def write_manifest(self, uuid, manifest):
        self.write_entity("manifests", uuid, "system", "list:manifests", manifest)

    def clean_manifests(self):
        return self.clean_entities("manifests", "system", "list:manifests")

    #======================================================================================
    """
        Runlists
    """

    def write_runlist(self, runlist_name, runlist):
        self.write_entity("runlists", runlist_name, "system", "list:runlists", runlist)

    def read_runlist(self, runlist_name, default=None):
        try:
            return self.read(self.key("runlists", runlist_name))
        except RuntimeError:
            return default

    def read_runlists(self):
        res = self.read_entities("runlists", "system", "list:runlists")
        return res

    def delete_runlist(self, runlist_name):
        runlists = self.read_runlists()
        if runlist_name not in runlists:
            return 
        self.delete_entity("runlists", runlist_name, "system", "list:runlists")

    def clean_runlists(self):
        runlists =  self.clean_entities("runlists", "system", "list:runlists")

        #clean invalid apps from runlists
        for runlist_name, runlist in runlists.items():
            for app_uuid, profile_name in runlist.items():
                try:
                    self.read(self.key("apps", app_uuid))
                except RuntimeError:
                    del runlists[runlist_name][app_uuid]

                try:
                    self.read(self.key("profiles", profile_name))
                except RuntimeError:
                    runlists[runlist_name][app_uuid] = 'default'

        for runlist_name, runlist in runlists.items():
            self.write(self.key("runlists", runlist_name), runlist)

        self.write(self.key("system", "list:runlists"), runlists.keys())
    #====================================================================================
    """
        Profiles
    """

    def write_profile(self, profile_name, profile):
        self.write_entity("profiles", profile_name, "system", "list:profiles", profile)

    def read_profiles(self):
        return self.read_entities("profiles", "system", "list:profiles")

    def delete_profile(self, profile):
        profiles = self.read_profiles()
        if profile not in profiles:
            return
        self.delete_entity("profiles", profile, "system", "list:profiles")

    def read_profile(self, profile_name, default=None):
        try:
            return self.read(self.key('profiles', profile_name))
        except RuntimeError:
            return default

    def clean_profiles(self):
        return self.clean_entities("profiles", "system", "list:profiles")

    #================================================================================
    """
        Hosts
    """

    def read_hosts(self):
        hosts_key = self.key('system', "list:hosts")
        try:
            hosts = dict(self.read(hosts_key))
        except RuntimeError:
            hosts = {}
        return hosts

    def write_hosts(self, hosts):
        self.write(self.key('system', "list:hosts"), hosts)

    def add_host(self, alias, host):
        hosts = self.read_hosts()
        #hosts.setdefault(alias, ).append(host)
        # why tuple instead list
        l = hosts.get(alias)
        if l is None:
            l = list()
        else:
            l = list(l)
        l.append(str(host))
        hosts[alias] = tuple(l)
        self.write_hosts(hosts)

    def delete_host(self, alias, host):
        hosts = self.read_hosts()
        if alias not in hosts:
            return
        l = hosts.get(alias)
        if l is None:
            return
        else:
            l = list(l)
        if host in l:
            l.remove(host)
        hosts[alias] = l
        self.write_hosts(hosts)

    def clean_hosts(self):
        hosts = self.read(self.key('system', "list:hosts"))
        if not isinstance(hosts, dict):
            self.write(self.key('system', "list:hosts"), {})

    def delete_alias(self, alias):
        hosts = self.read_hosts()
        if alias not in hosts:
            return
        hosts.pop(alias)
        self.write_hosts(hosts)

    #=====================================================================
    """
        Username operations
    """
    def find_user_by_username(self, username):
        try:
            return self.read(self.key('users', username))
        except RuntimeError:
            return None

    def find_user_by_token(self, token):
        try:
            username = self.read(self.key('tokens', token))
        except RuntimeError:
            return None

        return self.find_user_by_username(username)

    def get_username_by_token(self, token):
        try:
            username = self.read(self.key('tokens', token))
        except RuntimeError:
            return None
        else:
            return username

    #==================================================================
    """
        App operations
    """

    def save_app(self, uuid, data):
        self.write(self.key("apps", uuid), data.read())

    def delete_app(self, uuid):
        self.list_remove("system", "list:manifests", uuid)
        self.remove(self.key('manifests', uuid))
        self.remove(self.key('apps', uuid))

    #=================================================================
    """
        Host recipes
    """

    def write_recipes(self, host, data):
        pass
