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

import msgpack
from tornado.concurrent import Future

from cocaine.services import Service
from cocaine.exceptions import ChokeEvent

from cocaine.flow.token import Token

null_arg = msgpack.packb(None)


class PermissionDenied(Exception):
    pass


def convert_future(cocaine_future):
    future = Future()

    def handler(res):
        try:
            future.set_result(res.get())
        except ChokeEvent:
            if not future.done():
                future.set_result(None)
        except Exception as err:
            future.set_exception(err)

    cocaine_future.then(handler)
    return future


class FlowCloud(object):
    app = Service("flow-tools")
    token = Token()

    def __init__(self, user):
        self.user = user

    @staticmethod
    def authorized(token):
        user_info = FlowCloud.token.valid(token)
        return FlowCloud(user_info['name'])

    @staticmethod
    def guest():
        return FlowCloud("guest")

    def enqueue(self, method, *args):
        packed_args = msgpack.packb(*args) if args else null_arg
        return convert_future(self.app.enqueue(method,
                                               packed_args))

    # profiles
    def profile_list(self):
        return self.enqueue("profile-list")

    def profile_read(self, name):
        return self.enqueue("profile-read", name)

    def profile_upload(self, name, body):
        task = {
            "profilename": name,
            "profile": body,
        }
        return self.enqueue("profile-upload", task)

    def profile_remove(self, name):
        return self.enqueue("profile-remove", name)

    #hosts
    def host_list(self):
        return self.enqueue("host-list")

    def host_add(self, name):
        return self.enqueue("host-add", name)

    def host_remove(self, name):
        return self.enqueue("host-remove", name)

    # runlists
    def runlist_list(self):
        return self.enqueue("runlist-list")

    def runlist_read(self, name):
        return self.enqueue("runlist-read", name)

    def runlist_remove(self, name):
        return self.enqueue("runlist-remove", name)

    # routing groups
    def group_list(self):
        return self.enqueue("group-list")

    def group_read(self, name):
        return self.enqueue("group-read", name)

    def group_remove(self, name):
        return self.enqueue("group-remove", name)

    def group_create(self, name):
        return self.enqueue("group-create", name)

    def group_pushapp(self, name, app, weight):
        task = {
            "name": name,
            "app": app,
            "weight": weight,
        }
        return self.enqueue("group-pushapp", task)

    def group_popapp(self, name, app):
        task = {
            "name": name,
            "app": app,
        }
        return self.enqueue("group-popapp", task)

    def group_refresh(self, name):
        return self.enqueue("group-refresh", name)

    # crashlogs
    def crashlog_list(self, name):
        return self.enqueue("crashlog-list", name)

    def crashlog_view(self, name, timestamp):
        task = {
            "name": name,
            "timestamp": timestamp,
        }
        return self.enqueue("crashlog-view", task)

    # auth
    def signup(self, name, password):
        task = {
            "name": name,
            "password": password,
        }
        return self.enqueue("user-signup", task)

    def signin(self, name, password):
        task = {
            "name": name,
            "password": password,
        }
        return self.enqueue("user-signin", task)

    def gentoken(self, name, password):
        user_info = {
            "name": name,
            "password": password,
        }
        return self.token.pack_user(user_info)

    def user_remove(self, name):
        if name == self.user:
            return self.enqueue("user-remove", name)
        else:
            raise PermissionDenied("Unable to remove user %s." % name)

    #buildlogs
    def buildlog_list(self, username):
        return self.enqueue("user-buildlog-list", username)

    def buildlog_read(self, bl_id):
        return self.enqueue("user-buildlog-read", bl_id)
