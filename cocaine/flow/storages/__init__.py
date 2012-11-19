# -*- coding: utf-8 -*-
from __future__ import absolute_import
from werkzeug.local import LocalProxy
from .elliptics import Elliptics
from flask import current_app
from storages.mongo import Mongo


def connect_to_database(app):
    if app.config['STORAGE'] == 'elliptics':
        return Elliptics(app.config['ELLIPTICS_NODES'], app.config['ELLIPTICS_GROUPS'])
    elif app.config['STORAGE'] == 'mongo':
        return Mongo(app)
    raise ValueError('Unsupported type of storage')


def get_storage():
    return current_app.storage


def init_storage(app):
    app.storage = connect_to_database(app)


storage = LocalProxy(get_storage)
