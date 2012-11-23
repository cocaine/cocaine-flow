# -*- coding: utf-8 -*-
from pymongo.errors import DuplicateKeyError
from flask.ext.pymongo import PyMongo
from .storage import Storage
from storages.exceptions import UserExists

class Mongo(Storage):
    def __init__(self, app):
        self.app = app
        self.mongo = PyMongo(self.app)

    def create_user(self, username, hashed_password, admin, token):
        try:
            return self.mongo.db.users.insert(
                {'_id': username, 'password': hashed_password, 'admin': admin, 'token': token},
                safe=True)
        except DuplicateKeyError:
            raise UserExists

    def find_user_by_token(self, token):
        return self.mongo.db.users.find_one({'token': token})

    def find_user_by_username(self, username):
        return self.mongo.db.users.find_one({'_id': username})

    def key(self, key, *args):
        prefix = key
        postfix = args[0]

        if type(postfix) in set([tuple, list, set]):
            return type(postfix)(["%s\0%s" % (prefix, p) for p in postfix])

        return "%s\0%s" % (prefix, postfix)

    def read_manifest(self, uuid, default=None):
        return self.mongo.db.manifests.find_one({'uuid': uuid}) or default

    def read_manifests(self):
        return dict([(manifest['_id'], manifest) for manifest in self.mongo.db.manifests.find()])

    def write_manifest(self, uuid, manifest):
        return self.mongo.db.manifests.update({'_id': uuid}, manifest, upsert=True)

    def write_runlist(self, runlist_name, runlist):
        return self.mongo.db.manifests.update({'_id': runlist_name}, runlist, upsert=True)

    def read_runlists(self):
        return dict([(runlist['_id'], runlist) for runlist in self.mongo.db.runlists.find()])

    def read_runlist(self, runlist_name, default=None):
        return self.mongo.db.runlists.find_one({'_id': runlist_name}) or default

    def read_profile(self, profile_name, default=None):
        return self.mongo.db.profiles.find_one({'_id': profile_name}) or default

    def read_profiles(self):
        rv = {}
        for profile in self.mongo.db.profiles.find():
            _id = profile.pop('_id')
            rv[_id] = profile
        return rv

    def write_profile(self, profile_name, profile):
        profile['_id'] = profile_name
        return self.mongo.db.profiles.update({'_id': profile_name}, profile, upsert=True)

    def read_hosts(self):
        hosts = {}
        try:
            for record in self.mongo.db.hosts.find():
                hosts[record['alias']] = record['hosts']
        except RuntimeError:
            pass
        return hosts

    def add_host(self, alias, host):
        record = self.mongo.db.hosts.find_one({'alias': alias})
        if record is None:
            return self.mongo.db.hosts.insert({'alias': alias, 'hosts': [host]})

        if host in record['hosts']:
            return

        record['hosts'].append(host)
        return self.mongo.db.hosts.insert(record)

    def save_app(self, uuid, fileobj):
        self.mongo.save_file(self.key("apps", uuid), fileobj)

    def remove_app(self, uuid):
        self.mongo.remove_file(self.key("apps", uuid))
        self.mongo.db.manifests.remove({'uuid': uuid})

    def clean_manifests(self):
        pass
