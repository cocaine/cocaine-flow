# encoding: utf-8
#
#    Copyright (c) 2011-2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import uuid
import hashlib
from functools import partial

from Crypto.Hash import HMAC
import msgpack


from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger

namespace_prefix = "flow-users@"
USER_TAG = ["FLOW_USER"]
LOG_TAG = ["FLOW_UPLOAD_LOG"]

encoder = msgpack.packb
decoder = msgpack.unpackb

logger = Logger()


class SecureStorage(object):
    def __init__(self, storage):
        self.storage = storage

    @asynchronous
    def write(self, namespace, key, blob, tags):
        yield self.storage.write(namespace, key, encoder(blob), tags)

    @asynchronous
    def read(self, namespace, key):
        res = yield self.storage.read(namespace, key)
        yield decoder(res)

    @asynchronous
    def find(self, namespace, tags):
        yield self.storage.find(namespace, tags)

    @asynchronous
    def remove(self, namespace, key):
        yield self.storage.remove(namespace, key)

    def raw_storage(self):
        return self.storage


class UserDB(object):
    def __init__(self, storage, key, namespace):
        self.storage = SecureStorage(storage)
        self.key = key
        self.logger = Logger()
        self.namespace = namespace_prefix + namespace
        self.dbnamespace = namespace_prefix + "apps"
        self.lognamespace = namespace_prefix + "logs"
        self.logger.info("UserDB has been initialized. Use namespace %s"
                         % self.namespace)

    @asynchronous
    def exists(self, name):
        try:
            yield self.storage.read(self.namespace, name)
        except Exception as err:
            self.logger.error(str(err))
            yield False
        else:
            yield True

    @asynchronous
    def get(self, name):
        yield self.storage.read(self.namespace, name)

    @asynchronous
    def create(self, info):
        user_info = dict()
        uid = uuid.uuid4().hex
        name = info['name']
        password = info['password']

        exists = yield self.exists(name)
        if exists:
            raise Exception("Already exists")
        # Store user uid
        user_info['uid'] = uid
        # Store username
        user_info['name'] = name
        # Crypt user passwd
        h = HMAC.new(uid)
        h.update(password)
        user_info['hash'] = h.hexdigest()
        try:
            yield self.storage.write(self.namespace, name, user_info, USER_TAG)
        except Exception as err:
            self.logger.error(str(err))
            yield False
        else:
            yield True

    @asynchronous
    def remove(self, name):
        try:
            self.logger.info("Remove user %s" % name)
            yield self.storage.remove(self.namespace, name)
        except Exception as err:
            self.logger.error(repr(err))

        try:
            self.logger.info("Remove user %s application info" % name)
            yield self.storage.remove(self.dbnamespace, name)
        except Exception as err:
            self.logger.error(repr(err))

        try:
            self.logger.info("Remove user %s upload logs" % name)
            tags = LOG_TAG + [name]
            logkeys = yield self.storage.find(self.lognamespace, tags)
            self.logger.debug("Uploadlogs keys %s" % logkeys)
            for key in logkeys:
                yield self.storage.remove(self.lognamespace, key)
        except Exception as err:
            self.logger.error(repr(err))

    @asynchronous
    def login(self, name, password):
        user_info = yield self.get(name)
        self.logger.info(str(user_info))
        h = HMAC.new(user_info['uid'])
        h.update(password)
        self.logger.error("%s %s" % (h.hexdigest(), user_info['hash']))
        if (h.hexdigest() == user_info['hash']):
            user_info.pop('uid')
            yield user_info
        else:
            raise Exception("Invalid pair of login/password")

    @asynchronous
    def users(self):
        yield self.storage.find(self.namespace, USER_TAG)

    @asynchronous
    def user_apps(self, user):
        apps = list()
        try:
            raw_apps = yield self.storage.read(self.dbnamespace, user)
            apps = msgpack.unpackb(raw_apps)
        except Exception as err:
            self.logger.error(repr(err))
        finally:
            yield apps

    @asynchronous
    def write_app_info(self, user, name):
        def handler(data):
            apps = list()
            if data is None:
                apps = list()
            else:
                apps = msgpack.unpackb(data)

            if name in apps:
                self.logger.error("App %s already exists" % name)
                return None

            apps.append(name)
            return msgpack.packb(apps)

        reader = partial(self.storage.read, self.dbnamespace, user)
        writer = lambda result: self.storage.write(self.dbnamespace,
                                                   user,
                                                   result,
                                                   USER_TAG)
        yield self.quasi_atomic_write(reader, writer, handler)

    @asynchronous
    def write_buildlog(self, user, key, logdata):
        tags = LOG_TAG + [user]
        yield self.storage.write(self.lognamespace, key, logdata, tags)

    @asynchronous
    def read_buildlog(self, key):
        yield self.storage.read(self.lognamespace, key)

    @asynchronous
    def list_buildlog(self, user):
        tags = [user] if user else LOG_TAG
        yield self.storage.find(self.lognamespace, tags)

    @asynchronous
    def quasi_atomic_write(self, reader, writer, handler):
        while True:
            data = None
            summ = ""
            try:
                data = yield reader()
                summ = hashlib.md5(data).hexdigest()
            except Exception as err:
                self.logger.error(repr(err))

            result = handler(data)
            if result is None:
                break

            try:
                data = yield reader()
            except Exception as err:
                self.logger.error(repr(err))

            if data is None or summ == hashlib.md5(data).hexdigest():
                self.logger.info("MD5 is still valid. Do write")
                yield writer(result)
                break

            self.logger.info("MD5 mismatchs. Continue")
