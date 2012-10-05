# -*- coding: utf-8 -*-
import logging
import msgpack
from cocaine.flow.storages import storage


logger = logging.getLogger()


def read_hosts():
    hosts_key = storage.key('system', "list:hosts")
    try:
        hosts = dict(storage.read(hosts_key))
    except RuntimeError:
        hosts = {}
    return hosts


def write_hosts(hosts):
    storage.write(storage.key('system', "list:hosts"), hosts)


def remove_prefix(prefix, key):
    prefix = "%s\0" % prefix
    if isinstance(key, dict):
        return dict((k.replace(prefix, ''), v) for k, v in key.items())

    return key.replace(prefix, '')


def list_add(prefix, postfix, value, raise_on_missed_key=False):
    storage_key = storage.key(prefix, postfix)
    try:
        logger.info("Reading from elliptics %s", storage_key)
        entities = set(storage.read(storage_key))
    except RuntimeError:
        if raise_on_missed_key: raise
        entities = set()

    if value not in entities:
        entities.add(value)
        logger.info("Adding `%s` to list of entities by key %s" % (value, prefix + postfix))
        storage.write(storage_key, list(entities))


def list_remove(prefix, postfix, value):
    s = storage

    list_key = storage.key(prefix, postfix)
    entities = set(s.read(list_key))

    if value in entities:
        entities.remove(value)

        # removing manifest from manifest list
        s.write(list_key, list(entities))


def dict_remove(prefix, postfix, value):
    dict_key = storage.key(prefix, postfix)
    runlist_dict = storage.read(dict_key)
    runlist_dict.pop(value, None)
    storage.write(dict_key, runlist_dict)


def read_entities(prefix, list_prefix, list_postfix):
    s = storage
    entities = s.bulk_read(s.key(prefix, s.read(s.key(list_prefix, list_postfix))))
    entities = remove_prefix(prefix, entities)
    for k, entity in entities.items():
        entity_unpacked = msgpack.unpackb(entity)
        entities[k] = entity_unpacked
    return entities
