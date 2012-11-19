# -*- coding: utf-8 -*-
import msgpack

def serialize(func):
    def wrapper(key, data, *args, **kwargs):
        return func(key, msgpack.packb(data), *args, **kwargs)

    return wrapper


def deserialize(func):
    def wrapper(*args, **kwargs):
        return msgpack.unpackb(func(*args, **kwargs))

    return wrapper


class Storage(object):
    storage = None
    deserialize_methods = set(['read', 'read_data'])
    serialize_methods = set(['write', 'write_data'])

    def __getattr__(self, item):
        if item in self.deserialize_methods:
            return deserialize(getattr(self.storage, item))

        if item in self.serialize_methods:
            return serialize(getattr(self.storage, item))

        return getattr(self.storage, item)

    def key(self, prefix, postfix):
        raise NotImplemented

    def create_user(self, username, hashed_password, admin, token):
        raise NotImplementedError

    def find_user_by_token(self, token):
        raise NotImplementedError

    def find_user_by_username(self, username):
        raise NotImplementedError

    def read_manifest(self, uuid):
        raise NotImplementedError

    def read_manifests(self):
        raise NotImplementedError

    def read_runlists(self):
        raise NotImplementedError

    def read_runlist(self, runlist_name, default=None):
        raise NotImplementedError

    def read_profile(self, profile_name, default=None):
        raise NotImplementedError

    def read_profiles(self):
        raise NotImplementedError

    def read_hosts(self):
        raise NotImplementedError

    def write_profile(self, profile_name, profile):
        raise NotImplementedError

    def clean_manifests(self):
        pass

    def clean_runlists(self):
        pass

    def clean_profiles(self):
        pass

    def clean_hosts(self):
        pass

