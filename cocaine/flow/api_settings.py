# -*- coding: utf-8 -*-

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_REPLICA_SET = 'cocaine-dev'

SECRET_KEY = 'cocaines'

MAX_CONTENT_LENGTH = 16 * 1024 * 1024
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['.gz'])

HOSTNAME="127.0.0.1"
PORT = 5000

STORAGE = 'elliptics'

ELLIPTICS_NODES = {
    "el01.dev.yandex.net": 1025,
    "el02.dev.yandex.net": 1025,
}

ELLIPTICS_GROUPS = [1,2,3]
