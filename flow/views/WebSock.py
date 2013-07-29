import logging
import shutil
import hashlib
import json
from functools import partial

from tornadio2 import SocketConnection
from tornadio2 import TornadioRouter
from tornadio2 import event

from flow.utils.asyncprocess import asyncprocess
from flow.utils.storage import Storage
from flow.utils.helpers import get_applications
from flow.utils.helpers import get_user
from flow.utils.helpers import store_user

from cocaine.futures.chain import Chain

APP_LOGGER = logging.getLogger()


def dispatch(**gl_kwargs):
    def decorator(func):
        def wrapper(self, method, *args, **kwargs):
            job = gl_kwargs.get(method)
            if job:
                job(self, *args, **kwargs)
            else:
                func(self, method, *args, **kwargs)
        return wrapper
    return decorator


# EVENT: apps
def apps_get(self, *args):
    Chain([partial(get_applications,
                   partial(self.emit, "apps"))])


# EVENT: users
def users_get(self, data, *args, **kwargs):
    """on login or validation username
    {"name":"users","args":
        ["get",{"username":"login","password":"999999999999",
        "meta":{"query":"{\"username\":\"login\",
        \"password\":\"999999999999\"}"}}]}
    """
    user = data['username']
    password = data.get('password')
    key = data['meta']['query']
    APP_LOGGER.debug('Read user %s, key %s', user, key)
    Chain([partial(get_user,
                   partial(self.emit, 'users/%s' % key),
                   user, password)])


# EVENT: user
def user_get(self, data, *args, **kwargs):
    ''' Analog of user/me '''
    # Check cookies here
    print self.connection_info  # Extract cookie!
    user = False
    if not user:
        self.emit("user/me",
          {"user": {
          "id": "me",
          "username": "arkel",
          "status": "OK",
          "ACL": {}
          }})
    else:
        self.emit("user/me", {"user": {
                              "status": "fail",
                              "id": "me"}})
    return


def user_post(self, data, *args, **kwargs):
    try:
        user_info = data['user']
        username = user_info['username']
        password = user_info['password']
        name = user_info['name']
    except KeyError as err:
        APP_LOGGER.error("Missing argument, %s", str(err))
        return

    APP_LOGGER.info('Create user: %s', username)
    key = data['meta']['query']
    APP_LOGGER.warning("event: user, method: post, key: %s", key)
    Chain([partial(store_user,
                   partial(self.emit, "user/%s" % key),
                   username,
                   password, name=name)])


class WebSockInterface(SocketConnection):

    def __init__(self, *args, **kwargs):
        super(WebSockInterface, self).__init__(*args, **kwargs)
        self.connection_info = None

    def on_open(self, info):
        # TBD: place into active sessions
        print 'Client connected'
        self.connection_info = info

    def on_close(self):
        print 'Client disconnected'

    @event('users')
    @dispatch(get=users_get)
    def users(self, method, *args, **kwargs):
        """implemetns in decorator"""
        APP_LOGGER.error("Not implemented method %s", method)
        raise NotImplementedError("Not implemented method %s" % method)

    @event('user')
    @dispatch(get=user_get, post=user_post)
    def user(self, method, data):
        APP_LOGGER.error("Not implemented method %s", method)
        raise NotImplementedError("Not implemented method %s" % method)

    @event('profiles')
    def profiles(self, *args):
        print "profiles", args
        self.emit("profiles", {"profiles": [{
                "id": 1,
                "name": "default",
                "heartbeatTimeout": 21,
                "idleTimeout": 1,
                "startupTimeout": 2,
                "terminationTimeout": 0,

                "concurrency": 4,
                "crashlogLimit": 10,
                "growThreshold": 40,
                "poolLimit": 30,
                "queueLimit": 20,
                "logOutput": False
            }]})

    @event('profile')
    def profile(self, meth, profile_id, *args, **kwargs):
        APP_LOGGER.debug("PROFILE %s %s", meth, profile_id)
        if meth == 'get':
            self.emit("profile/%s" % profile_id, {"profile": {
                "id": 1,
                "name": "default",
                "heartbeatTimeout": 21,
                "idleTimeout": 1,
                "startupTimeout": 2,
                "terminationTimeout": 0,
                "concurrency": 4,
                "crashlogLimit": 10,
                "growThreshold": 40,
                "poolLimit": 30,
                "queueLimit": 20,
                "logOutput": False
                }})
        else:
            print "PROFILE PUT"

    @event('clusters')
    def clusters(self, *args):
        print "clusters", args
        self.emit("clusters", {"clusters": [{
                "id": 1,
                "name": "default"
            },{
                "id": 2,
                "name": "favorite"
            }, {
                "id": 3,
                "name": "heavy"
            }]})

    @event("app")
    def app(self, method, app_id, **kwargs):
        print "ZZZ", app_id
        if method == "get":
            def wr(obj):
                try:
                    data = yield Storage().read_app_future(app_id)
                    obj.emit("app/%s" % app_id, {"app" : json.loads(data), "commits" : {
                            "id": 1,
                            "summary": 1,
                            "app": app_id,
                            "page": 1,
                            "hash": "c43733",
                            "link": "https://github.com/...", 
                            "date": 1368486236487, 
                            "message": "TTTT",
                            "author": "Oleg <markelog@gmail.com>",
                            "active": True,
                            "last": False
                    }})
                except Exception as err:
                    print err
            Chain([partial(wr, self)])
            print "TTTT"
        else:
            print "app update", method, app_id


    @event('upload')
    def upload(self, data):
        url, vcs_type, ref = (_["value"] for _ in data)
        if ref == '':
            ref = "HEAD"
        self.emit("upload", {"message": "Clone repository", "percentage": 0})
        path = "/tmp/COCAINE_FLOW"
        try:
            shutil.rmtree(path)
        except OSError as err:
            print err

        g = on_git_clone(self, url, vcs_type, ref, path)
        g.next()
        asyncprocess(self,
                    # REPLACE WITH REAL URL
                    "git clone https://github.com/cocaine/cocaine-flow %s --progress" % path,
                    g.send)

    @event('apps')
    @dispatch(get=apps_get)
    def apps(self, method, *args):
        """implemetns in decorator"""
        APP_LOGGER.error("Not implemented method %s" % method)
        raise NotImplementedError("Not implemented method %s" % method)

    @event('summary')
    def summary(self, method, app_id):
        APP_LOGGER.debug("Event summary, method %s, app_id %s" % (method, app_id))
        self.emit("summary/%s" % app_id, {"summary": {
                    "id": 1,
                    "app": 1,
                    "commits": [1, 2],

                    "repository": "git://github.yandex-team.ru/user/application.git",
                    "address": "test",
                    "developers": "admin, tester",
                    "tracker": "some tracker",
                    "dependencies": "sh==1.02, msgpack-python",
                    "use-frequency": "often"},
                    "commits" : {
                            "id": 1,
                            "summary": 1,
                            "app": app_id,
                            "page": 1,
                            "hash": "c43733",
                            "link": "https://github.com/...", 
                            "date": 1368486236487, 
                            "message": "TTTT",
                            "author": "Oleg <markelog@gmail.com>",
                            "active": True,
                            "last": False
                    }}
            )

    @event('commits')
    def commits(self, method, args, *t, **kwargs):
        print args
        #print kwargs
        self.emit(r"commits/%s" % (args['meta']['query']),
                 {"commits" : [{
                "id": 2,
                "summary": args['summary'],
                "app":  "MY_APP_IDe15e216fc1c639f787b1231ecdfa1bf8",
                "page": 2,
                "hash": "a044a3",
                "link": "https://github.com/...",
                "date": 1366630011651,
                "message": "message",
                "author": "Oleg <markelog@gmail.com>",
                "active": False,
                "last": True
            }]})

    @event('graphs')
    def graphs(self, method, *args, **kwargs):
        print args



    @event('deploy')
    def deploy(self, method, app_id, *args, **kwargs):
        APP_LOGGER.info("deploy, %s" % app_id)
        import time
        if method == "post":
            self.emit("deploy/%s" % app_id, {"message": "A",
                                             "percentage": 20})
            time.sleep(0.5)
            self.emit("deploy/%s" % app_id, {"message": "b",
                                             "percentage": 40})
            time.sleep(0.5)
            self.emit("partial/app/%s" % app_id, {"app": {"status": "OK",
                                                  "status-message": "normal",
                                                  "id": app_id}})
            self.emit("deploy/%s" % app_id, {"message": "c",
                                             "percentage": 100,
                                             "finished": True,
                                             "id": app_id})  # Add arrayof cms

    @event('keepalive/deploy')
    def partial_deploy(self, method, app_id, *args):
        print method, app_id, args



def on_git_clone(obj, url, vcs_type, ref, path):
    """Upload from git process"""
    msg = ["Cloning %s\r\n" % url, "", "", "", ""]
    while True:
        data = yield
        if data is not None:
            for line in data.split('\r'):
                if "Counting objects" in line:
                    msg[1] = line
                    prog = 25
                elif "Compressing objects" in line:
                    msg[2] = line
                    prog = 40
                elif "Receiving objects:" in line:
                    msg[3] = line
                    prog = 60
                elif "Resolving deltas:" in line:
                    msg[4] = line
                    prog = 75
                obj.emit("upload", {"message": ''.join(msg),
                                    "percentage": prog})
        else:
            break
    # for test app name
    app_id = "MY_APP_ID" + hashlib.md5(str(ref)).hexdigest()
    app_info = {"name": app_id,
                "id": app_id,
                "reference": ref,
                "status": "OK",
                "profile": 1,
                "status-message": "normal"}

    print app_info
    # Make tar.gz
    msg.append("Make tar.gz\n")
    obj.emit("upload", {"message": ''.join(msg),
                        "percentage": 90})
    shutil.make_archive("%s/%s" % (path, app_id),
                        "gztar", root_dir=path,
                        base_dir=path, logger=APP_LOGGER)

    # Store archive
    msg.append("Store archive\n")
    obj.emit("upload", {"message": ''.join(msg),
                        "percentage": 95})
    Storage().write_apps_data(partial(on_app_data_upload,
                                      obj, app_id,
                                      msg, app_info),
                              app_id,
                              open("%s/%s.tar.gz" % (path, app_id),
                                   'rb').read())



def on_app_data_upload(obj, app_id, msg, app_info, res):
    APP_LOGGER.info(res)
    APP_LOGGER.info(app_info)
    msg.append("Store information about application\n")
    obj.emit("upload", {"message": ''.join(msg),
                        "percentage": 98})
    Storage().write_apps(partial(on_app_upload, obj, app_id, msg),
                         app_id,
                         json.dumps(app_info))



def on_app_upload(obj, app_id, msg, res):
    APP_LOGGER.info(res)
    msg.append("Done\n")
    obj.emit("upload", {"finished": True,
                        "id": app_id,
                        "percentage": 100,
                        "message": ''.join(msg)})

# Create TornadIO2 router
Router = TornadioRouter(WebSockInterface)

