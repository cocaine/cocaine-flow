# encoding: utf-8
#
#    Copyright (c) 2013-2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2013-2014 Other contributors as noted in the AUTHORS file.
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
import threading

import msgpack
from tornado.concurrent import Future
from cocaine.exceptions import ChokeEvent


null_arg = msgpack.packb(None)


class PermissionDenied(Exception):
    pass


class AppUploadInfo(object):

    @classmethod
    def configure(cls, docker, registry):
        cls.docker = docker
        cls.registry = registry

    def __init__(self, appname, version, path):
        self.appname = appname
        self.version = version
        self.path = path

    def fullname(self):
        return "%s_%s" % (self.appname, self.version)

    def routing_group(self):
        return self.appname

    def to_task(self):
        return {
            "path": self.path,
            "app": self.appname,
            "version": self.version,
            "docker": self.docker,
            "registry": self.registry,
        }


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


class FlowTools(object):
    _instance_lock = threading.Lock()

    @staticmethod
    def instance(host="localhost", port=10053):
        if not hasattr(FlowTools, "_instance"):
            with FlowTools._instance_lock:
                if not hasattr(FlowTools, "_instance"):
                    from cocaine.services import Service
                    FlowTools._instance = Service("flow-tools",
                                                  host=host,
                                                  port=port)
        return FlowTools._instance


class FlowCloud(object):
    def __init__(self, user_info):
        self.app = FlowTools.instance()
        self.user_info = user_info
        self.user = user_info['name']

    @staticmethod
    def authorized(user_info):
        return FlowCloud(user_info)

    @staticmethod
    def guest():
        user_info = {
            "name": "guest"
        }
        return FlowCloud(user_info)

    def enqueue(self, method, *args):
        packed_args = msgpack.packb(*args) if args else null_arg
        return convert_future(self.app.enqueue(method,
                                               packed_args))

    def stream_enqueue(self, method, *args):
        packed_args = msgpack.packb(*args) if args else null_arg
        return self.app.enqueue(method, packed_args)

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

    def user_remove(self, name):
        if name == self.user:
            return self.enqueue("user-remove", name)
        else:
            raise PermissionDenied("Unable to remove user %s." % name)

    # buildlogs
    def buildlog_list(self, username):
        return self.enqueue("user-buildlog-list", username)

    def buildlog_read(self, bl_id):
        return self.enqueue("user-buildlog-read", bl_id)

    # apps
    def app_list(self):
        return self.enqueue("user-app-list", self.user)

    def app_info(self, appname, version):
        task = {
            "appname": appname,
            "version": version,
            "username": self.user,
        }
        return self.enqueue("app-info", task)

    def app_upload(self, upload_info):
        task = upload_info.to_task()
        task['user'] = self.user
        return self.stream_enqueue("user-upload", task)
