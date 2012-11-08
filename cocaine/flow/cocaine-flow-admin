#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import getpass
from uuid import uuid4

import pymongo
import yaml
from elliptics import Logger, Node


def ask(what, hidden=False, empty=False, default=None):
    rv = None
    while not rv:
        if empty:
            msg = '%s (or empty): ' % what
        elif default is not None:
            msg = '%s (default: %s): ' % (what, default)
        else:
            msg = '%s: ' % what

        if hidden:
            rv = getpass.getpass(msg)
        else:
            rv = raw_input(msg)

        if not rv and empty:
            break

        if not rv and default is not None:
            rv = default
            break

        if not rv:
            print '%s cannot be empty' % what

    return rv


def install_admin_user(conn, username, password):
    try:
        conn['users'].insert(
            {'_id': username, 'password': hashlib.sha1(password).hexdigest(), 'admin': True, 'token': str(uuid4())},
            safe=True)
    except pymongo.errors.DuplicateKeyError:
        print 'Username is busy!'
        return False

    return True


def key(prefix, postfix):
    return "%s\0%s" % (prefix, postfix)


def main():
    etc_dir = '/etc/cocaine-flow'
    if not os.path.exists(etc_dir):
        try:
            os.mkdir(etc_dir)
        except OSError as e:
            print 'Unable to create dir %s. %s' % (etc_dir, e)
            sys.exit(1)

    settings_path = etc_dir + '/settings.yml'

    if not os.path.exists(settings_path) and not os.access(etc_dir, os.W_OK):
        print 'Write access to %s is required' % etc_dir
        sys.exit(1)

    if os.path.exists(settings_path) and not os.access(settings_path, os.W_OK):
        print 'Write access to %s is required' % settings_path
        sys.exit(1)

    username = ask('Username', default="admin")
    password = ask('Password', hidden=True, default='password')

    while True:
        mongo_hostname = ask('Mongo hostname', default='localhost')
        mongo_port = ask('Mongo port', default=27017)
        mongo_dbname = ask('Mongo db name', default='cocaine-flow')
        mongo_replica_set = ask('Mongo replica set', empty=True)

        kw = {}
        if mongo_replica_set:
            kw['replicaSet'] = mongo_replica_set
            connection_cls = pymongo.ReplicaSetConnection
        else:
            connection_cls = pymongo.Connection

        try:
            conn = connection_cls("%s:%s" % (mongo_hostname, mongo_port), **kw)
        except pymongo.errors.PyMongoError as e:
            print "Wrong mongo connection settings: %s!" % e
            continue

        if not install_admin_user(conn[mongo_dbname], username, password):
            username = ask('Username', default="admin")
            password = ask('Password', hidden=True, default='password')
            continue

        break

    # requires to refactor when support of other storages will be available
    # storage = ask('Storage', default="elliptics")
    while True:
        node = ask('Elliptics node (hostname[:port])', default="localhost:1025")
        groups = ask('Elliptics groups', default='1,2,3')
        node_split = node.split(':')

        if len(node_split) == 1:
            host = node_split[0]
            elliptics_port = 1025
        elif len(node_split) == 2:
            host = node_split[0]
            elliptics_port = node_split[1]
        elif len(node_split) == 3:
            host = node_split[0]
            elliptics_port = node_split[1]
        else:
            print 'Unable to recognize elliptics node!'
            continue

        try:
            node = Node(Logger("/tmp/cocainoom-elliptics.log"))
            node.add_remote(host, int(elliptics_port))
        except RuntimeError:
            print "Wrong elliptics connection settings!"
            continue

        try:
            from elliptics import Session

            storage = Session(node)
        except ImportError:
            storage = node

        groups = map(int, groups.split(','))
        storage.add_groups(groups)

        try:
            storage.read(key('system', 'list:runlists'))
        except RuntimeError:
            try:
                storage.write(key('system', 'list:runlists'), ['default'])
            except RuntimeError:
                print "Wrong elliptics connection settings!"
                continue

        break

    port = ask("Port", default=5000)

    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = yaml.load(f)
    else:
        settings = {}

    settings['PORT'] = port
    settings['SECRET_KEY'] = str(uuid4())
    settings['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    settings['UPLOAD_FOLDER'] = '/tmp'
    settings['ALLOWED_EXTENSIONS'] = ['.gz']
    settings['MONGO_HOST'] = mongo_hostname
    settings['MONGO_PORT'] = mongo_port
    settings['MONGO_DBNAME'] = mongo_dbname
    if mongo_replica_set:
        settings['MONGO_REPLICA_SET'] = mongo_replica_set
    settings['STORAGE'] = 'elliptics'
    settings['ELLIPTICS_NODES'] = {
        host: elliptics_port
    }
    settings['ELLIPTICS_GROUPS'] = groups

    with open(settings_path, 'w') as f:
        yaml.dump(settings, f)
    sys.exit(0)


if __name__ == '__main__':
    main()


