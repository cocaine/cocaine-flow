# -*- coding: utf-8 -*-
import logging
from cocaine.flow.storages import storage


logger = logging.getLogger()


def add_prefix(prefix, key):
    prefix = "%s\0" % prefix
    if isinstance(key, dict):
        return dict((prefix + k, v) for k, v in key.items())

    if type(key) in set([list, tuple]):
        return ["%s%s" % (str(prefix), str(v)) for v in key]

    return "%s%s" % (str(prefix), str(key))


def remove_prefix(prefix, key):
    prefix = "%s\0" % prefix
    if isinstance(key, dict):
        return dict((k.replace(prefix, ''), v) for k, v in key.items())

    return key.replace(prefix, '')


def dict_remove(prefix, postfix, value):
    dict_key = storage.key(prefix, postfix)
    runlist_dict = storage.read(dict_key)
    runlist_dict.pop(value, None)
    storage.write(dict_key, runlist_dict)
