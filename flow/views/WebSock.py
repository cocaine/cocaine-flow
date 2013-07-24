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

from cocaine.futures.chain import Chain

log = logging.getLogger()


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

def apps_get(self, *args):
    Chain([partial(get_applications,
                   partial(self.emit, "apps"))])


class WebSockInterface(SocketConnection):

    def on_open(self, info):
        # TBD: place into active sessions
        print 'Client connected'
        print info.ip
        print str(info.cookies)
        print info.arguments

    def on_close(self):
        print 'Client disconnected'

    @event('user/me')
    def user(self, *args):
        """ On failure - not now """
        self.emit("user/me",
                  {"user": {
                        "id": "me",
                        "username": "arkel",
                        "status": "OK",
                        "ACL": {}
                        }})

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
        log.debug("PROFILE %s %s" % (meth, profile_id))
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
                } })
        else:
            print "PROFILE PUT"
            #Storage().store_profile(partial(self.emit, {"profile": {
            #    "id" : 10
            #    }}))

    @event('clusters')
    def clusters(self, *args):
        print "clusters", args
        self.emit("clusters", {"clusters" : [{
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
        log.error("Not implemented method %s" % method)
        raise NotImplementedError("Not implemented method %s" % method)

    @event('summary')
    def summary(self, method, app_id):
        log.debug("Event summary, method %s, app_id %s" % (method, app_id))
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
    app_info = { "name": app_id,
                 "id" : app_id,
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
                        base_dir=path, logger=log)

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
    log.info(res)
    log.info(app_info)
    msg.append("Store information about application\n")
    obj.emit("upload", {"message": ''.join(msg),
                        "percentage": 98})
    Storage().write_apps(partial(on_app_upload, obj, app_id, msg),
                         app_id,
                         json.dumps(app_info))



def on_app_upload(obj, app_id, msg, res):
    log.info(res)
    msg.append("Done\n")
    obj.emit("upload", {"finished": True,
                        "id": app_id,
                        "percentage": 100,
                        "message": ''.join(msg)})

# Create TornadIO2 router
Router = TornadioRouter(WebSockInterface)

