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
