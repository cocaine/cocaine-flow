# -*- coding: utf-8 -*-
import logging
import msgpack
from flask import current_app


logger = logging.getLogger()


def read_hosts():
    hosts_key = key('system', "list:hosts")
    try:
        hosts = set(current_app.storage.read(hosts_key))
    except RuntimeError:
        hosts = set()
    return hosts


def write_hosts(hosts):
    current_app.storage.write(key('system', "list:hosts"), list(hosts))


def key(prefix, postfix):
    if type(postfix) in set([tuple, list, set]):
        return type(postfix)(["%s\0%s" % (prefix, p) for p in postfix])

    return "%s\0%s" % (prefix, postfix)


def remove_prefix(prefix, key):
    prefix = "%s\0" % prefix
    if isinstance(key, dict):
        return dict((k.replace(prefix, ''), v) for k, v in key.items())

    return key.replace(prefix, '')


def list_add(prefix, postfix, value, raise_on_missed_key=False):
    storage_key = key(prefix, postfix)
    try:
        logger.info("Reading from elliptics %s", storage_key)
        entities = set(current_app.storage.read(storage_key))
    except RuntimeError:
        if raise_on_missed_key: raise
        entities = set()

    if value not in entities:
        entities.add(value)
        logger.info("Adding `%s` to list of entities by key %s" % (value, prefix + postfix))
        current_app.storage.write(storage_key, list(entities))


def list_remove(prefix, postfix, value):
    s = current_app.storage

    list_key = key(prefix, postfix)
    entities = set(s.read(list_key))

    if value in entities:
        entities.remove(value)

        # removing manifest from manifest list
        s.write(list_key, list(entities))


def dict_remove(prefix, postfix, value):
    s = current_app.storage

    dict_key = key(prefix, postfix)
    runlist_dict = s.read(dict_key)
    runlist_dict.pop(value, None)
    s.write(dict_key, runlist_dict)


def read_entities(prefix, list_prefix, list_postfix):
    s = current_app.storage
    entities = s.bulk_read(s.key(prefix, s.read(s.key(list_prefix, list_postfix))))
    entities = remove_prefix(prefix, entities)
    for k, entity in entities.items():
        entity_unpacked = msgpack.unpackb(entity)
        entities[k] = entity_unpacked
    return entities
