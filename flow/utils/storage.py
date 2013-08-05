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

from cocaine.services import Service

FLOW_USERS = "cocaine_flow_users"
FLOW_USERS_TAG = "flow_users"

FLOW_PROFILES = "cocaine_flow_profiles"
FLOW_PROFILES_TAG = "flow_profiles"

FLOW_APPS_DATA = "cocaine_flow_apps_data"
FLOW_APPS_DATA_TAG = "flow_apps_data"

FLOW_APPS = "cocaine_flow_apps"
FLOW_APPS_TAG = "apps"


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

    # app
    def list_app_future(self):
        return self._storage.find(FLOW_APPS, [FLOW_APPS_TAG])

    def read_app_future(self, name):
        return self._storage.read(FLOW_APPS, name)

    def write_app_future(self, name, data):
        return self._storage.write(FLOW_APPS, name, data, [FLOW_APPS_TAG])

    def write_app_data_future(self, name, data):
        return self._storage.write(FLOW_APPS_DATA, name,
                                   data, [FLOW_APPS_DATA_TAG])

    # user
    def read_user_future(self, name):
        return self._storage.read(FLOW_USERS, name)

    def write_user_furure(self, name, data):
        return self._storage.write(FLOW_USERS, name, data, [FLOW_USERS_TAG])

    # profile
    def read_profile_future(self, name):
        return self._storage.read(FLOW_PROFILES, name)

    def write_profile_future(self, name, data):
        return self._storage.write(FLOW_PROFILES, name,
                                   data, [FLOW_PROFILES_TAG])

    def list_profile_future(self):
        return self._storage.find(FLOW_PROFILES, [FLOW_PROFILES_TAG])

    def delete_profile_future(self, name):
        return self._storage.remove(FLOW_PROFILES, name)
