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

import json

from tornado import web
from tornado import gen
from tornado.ioloop import IOLoop

from cocaine.tools.helpers._unix import AsyncUnixHTTPClient
from tornado.httpclient import AsyncHTTPClient


class Ping(web.RequestHandler):
    def get(self):
        self.write("Pong")


class Status(web.RequestHandler):
    @gen.coroutine
    def get(self):
        docker_res = {
            "status": "unavailable",
        }

        registry_res = {
            "status": "unavailable",
        }
        # alias
        self.docker = "%s/info" % self.application.docker
        self.registry = "http://%s/_ping" % self.application.registry

        registry_cli = AsyncHTTPClient()
        if self.docker.startswith("unix:"):
            docker_cli = AsyncUnixHTTPClient(IOLoop.current(), self.docker)
        else:
            docker_cli = registry_cli

        # fetch docker status
        docker_status = docker_cli.fetch(self.docker)

        # fetch registry status
        registry_status = registry_cli.fetch(self.registry)
        try:
            req = yield docker_status
            docker_res = json.loads(req.body)
        except Exception:
            pass

        try:
            req = yield registry_status
            if req.code == 200:
                registry_res["status"] = "OK"
        except Exception:
            pass

        self.write({"Docker": docker_res,
                    "Registry": registry_res})
