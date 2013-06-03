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
from functools import partial

from tornado.process import Subprocess
from tornado import web
from tornado.ioloop import IOLoop

from cocaine.services import Service
from cocaine.tools.tools import NodeInfoAction

from utils.route import Route
from utils.decorators import authorization_require

__all__ = ["Info"]

node = Service("node")
storage = Service("storage")

def t(output):
    print "Start"
    import time
    while True:
        output.send(time.time())
        print "Aaa"
        time.sleep(1)

@Route(r"/Apps")
class Info(web.RequestHandler):

    @web.asynchronous
    def get(self):
        info = NodeInfoAction(node)
        info.execute().bind(self.on_info, self.on_error)

    def on_info(self, chunk):
        self.write(chunk)
        self.finish()

    def on_error(self, excep):
        self.write(str(excep))
        self.finish()


#====================

import os
import sh
import json

def args_packer(func, pipe):
    def wrapper(fd, event):
        _input = pipe.read_from_fd()
        if _input is None:
            try:
                func(None)
            except StopIteration:
                pass
    return wrapper

def make_sh(command, me):
    p = Subprocess(command.split(' '), stdout=Subprocess.STREAM)
    fd = p.stdout.fileno()
    IOLoop.instance().add_handler(fd, args_packer(me.send, p.stdout), IOLoop.READ)

COMMITS_FIELD = ("hash", "author", "email", "data", "message")
import itertools

@Route(r"/Test")
class Test(web.RequestHandler):

    def async_write(self, data):
        self.write(data)
        self.flush()

    @web.asynchronous
    def get(self):
        g = self.on_data()
        g.next()
        g.send(g)
        
    def on_data(self):
        url = self.get_argument("url")
        self.async_write("<br> Start uploading\n</br>")
        me = yield

        # git clone
        base_clone_path = "/tmp"
        clone_path = "%s/%s" % (base_clone_path,os.path.basename(url))
        if os.path.exists(clone_path):
            sh.rm("-rf", clone_path)
        ref = "HEAD"
        self.async_write("Clone repository\n")
        make_sh("git clone %s %s" % (url, clone_path), me)

        yield 
        try:
            sh.git("rev-parse", ref, _cwd=clone_path).strip()
            commits = sh.git("--no-pager", "log", r"--pretty=format:%H||%an||%ae||%ad||%s", _cwd=clone_path).splitlines()
            print [dict((k,v) for k,v in itertools.izip(COMMITS_FIELD, commit.split('||'))) for commit in commits]
        except Exception as err:
            print err







