#
#   Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
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

import logging
from functools import wraps

import msgpack
from cocaine.services import Service

from utils.decorators import unwrap_result


class Singleton(type):

    def __init__(self, *args, **kwargs):
        self.__instance = None
        self.log = logging.getLogger()
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs): 
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


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
            self._storage.async_reconnect(on_reconnect, 1)
    return wrapper


def deserializer(func):
    @wraps(func)
    def wrapper(res):
        try:
            val = msgpack.unpackb(res)
        except Exception as err:
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

    def __init__(self):
        self._storage = Service("storage")
        self.log.info("Initialize storage successfully: %s" % self._storage.service_endpoint)

    @property
    def connected(self):
        return self._storage.connected

    @property
    def endpoint(self):
        return self._storage.service_endpoint

    @insure_connected
    def profiles(self, callback):
        self._storage.find("profiles", ["profile"]).then(callback)

    @deserialize_result
    @insure_connected
    def get_profile(self, callback, name):
        self._storage.read("profiles", name).then(unwrap_result(callback))

