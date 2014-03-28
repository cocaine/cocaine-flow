import threading

import msgpack
from tornado.concurrent import Future

from cocaine.services import Service
from cocaine.exceptions import ChokeEvent

null_arg = msgpack.packb(None)


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
    _instance_lock = threading.Lock()

    def __init__(self):
        self.app = Service("flow-tools")

    @staticmethod
    def instance():
        if not hasattr(FlowCloud, "_instance"):
            with FlowCloud._instance_lock:
                if not hasattr(FlowCloud, "_instance"):
                    # New instance after double check
                    FlowCloud._instance = FlowCloud()
        return FlowCloud._instance

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

    #buildlogs
    def buildlog_list(self, username):
        return self.enqueue("user-buildlog-list", username)

    def buildlog_read(self, bl_id):
        return self.enqueue("user-buildlog-read", bl_id)
