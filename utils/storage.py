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

import uuid

#from msgpack import packb as SERIALIZE
#from msgpack import unpackb as DESERIALIZE
from json import dumps as SERIALIZE
from json import loads as DESERIALIZE

from cocaine.services import Service
from cocaine.futures import NextTick

from utils.decorators import CocaineCoroutine

def serialize(data):
    # TBD - add crypt()
    return SERIALIZE(data)

def deserialize(data):
    # TDB - add encrypt()
    return DESERIALIZE(data)

__all__ = ["Storage"]

USERS_NAMESPACE = "flow_users"
USERS_TAG = "user"

PROFILES_NAMESPACE = "flow_profiles"
PROFILES_TAG = "profile"

MISC_NAMESPACE = "flow_misc"
MISC_TAG = "misc"


class Storage(object):

    def __init__(self, instance=None):
        self._storage = instance or Service("storage")

    # Users
    
    @CocaineCoroutine
    def create_user(self, login, passwod, response):
        res = yield self._storage.find(USERS_NAMESPACE, [USERS_TAG])
        if login in res:
            response.write("User %s exists" % login)
            response.finish()
            raise StopIteration

        uid = str(uuid.uuid4())
        data = {    "uid" : uid,
                    "login" : login,
                    "passwod" : passwod,
                    "ACL"  : True }
        yield self._storage.write(USERS_NAMESPACE, login, SERIALIZE(data), [USERS_TAG])

        response.write("Create user succefully")
        response.finish()

    # Profiles

    @CocaineCoroutine
    def profiles(self, response):
        profiles = yield self._storage.find(PROFILES_NAMESPACE, [PROFILES_TAG])
        res = dict()
        for profile in profiles:
            raw_profile = yield self._storage.read(PROFILES_NAMESPACE, profile)
            res[profile] = DESERIALIZE(raw_profile)
        response.write(res)
        response.finish()      

    @CocaineCoroutine
    def profile_add(self, name, profile, response):
        try:
            yield self._storage.write(PROFILES_NAMESPACE, name, SERIALIZE(profile), [PROFILES_TAG])      
        except Exception as err:
            response.write("Failed")
        else:
            response.write("Done")
        response.finish()

    @CocaineCoroutine
    def profile_remove(self, name, response):
        try:
            yield self._storage.remove(PROFILES_NAMESPACE, name)
        except Exception as err:
            print err
            response.write("Failed")
        else:
            response.write("DONE")
        response.finish()

