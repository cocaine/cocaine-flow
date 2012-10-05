# -*- coding: utf-8 -*-
from werkzeug.local import LocalProxy
from .elliptics import Elliptics
from flask import current_app


def connect_to_database(storage):
    if storage == 'elliptics':
        return Elliptics()
    raise ValueError('Unsupported type of storage')


def get_storage():
    return current_app.storage


def init_storage(app):
    app.storage = connect_to_database(app.config['STORAGE'])


storage = LocalProxy(get_storage)
