#
#   Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or
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

import logging
import hmac
from functools import wraps
import json
import uuid

SEREALIZE = json.dumps
DESEREALIZE = json.loads

import msgpack
from cocaine.services import Service

from flow.utils.decorators import unwrap_result, RewrapResult

from cocaine.exceptions import ChokeEvent

FLOW_USERS = "cocaine_flow_users"


class Singleton(type):

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super(Singleton, cls).__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


def insure_connected(func):
    def wrapper(self, callback, *args, **kwargs):
        if self.connected:
            return func(self, callback, *args, **kwargs)
        else:
            self.log.warning("Disconnected. Try reconnect")

            def on_reconnect(res):
                try:
                    res.get()
                    self.log.info("Reconnect to %s" % self.endpoint)
                    return func(self, callback, *args, **kwargs)
                except Exception as err:
                    self.log.error("Unable to reconnect %s" % str(err))
                    callback(res)
            self.backend.async_reconnect(on_reconnect, 1)
    return wrapper


def deserializer(func):
    @wraps(func)
    def wrapper(res):
        try:
            val = msgpack.unpackb(res)
        except Exception:
            return func(res)
        else:
            return func(val)
    return wrapper


def deserialize_result(func):
    @wraps(func)
    def wrapper(self, callback, *args):
        return func(self, deserializer(callback), *args)
    return wrapper


class Storage(object):

    __metaclass__ = Singleton

    log = logging.getLogger()

    def __init__(self):
        self._storage = Service("storage")
        self.log.info("Initialize storage successfully: %s"
                      % self._storage.service_endpoint)

    @property
    def connected(self):
        return self._storage.connected

    @property
    def endpoint(self):
        return self._storage.service_endpoint

    @property
    def backend(self):
        return self._storage

    @insure_connected
    def profiles(self, callback):
        self._storage.find("profiles", ["profile"]).then(callback)

    @deserialize_result
    @insure_connected
    def get_profile(self, callback, name):
        self._storage.read("profiles", name).then(unwrap_result(callback))

    def check_user(self, name):
        def wrapper(res):
            try:
                data = res.get()
                if len(data) > 0:
                    self.log.debug("user %s exists" % name)
                    return data
                else:
                    self.log.debug("user %s doesn't exist" % name)
                    return data  # [] is False
            except ChokeEvent:
                pass
                # print repr(err)
        return self._storage.find(FLOW_USERS, [name]).then(wrapper)

    def create_user(self, callback, name, passwd):
        self.log.info("Create user %s" % name)
        _uuid = str(uuid.uuid4())
        data = {"username": name,
                "id": _uuid,
                "ACL": {},
                "status": "ok",
                "passwd": hmac.new(_uuid, passwd).hexdigest()}

        def on_check(res):
            if not res.get():
                self.log.info("Create new user")
                self._storage.write(FLOW_USERS,
                                    _uuid,
                                    SEREALIZE(data),
                                    ["users", name]).then(callback)
            else:
                self.log.warning("User already exists")
                callback(RewrapResult("Already exists"))

        self.check_user(name).then(on_check)

    @insure_connected
    def find_user(self, callback, name):
        tag = name or "users"

        def on_check(_all):
            out = list()
            for i in _all.get():
                tmp = yield self._storage.read(FLOW_USERS, i)
                out.append(DESEREALIZE(tmp))
            callback(RewrapResult(out))

        self.check_user(tag).then(on_check)

    def remove_user(self, callback, name):
        self._storage.remove(FLOW_USERS, name).then(callback)
