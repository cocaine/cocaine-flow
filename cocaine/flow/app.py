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

import logging
from multiprocessing.pool import ThreadPool

import tornado.web
from tornado.ioloop import IOLoop

from cocaine.flow.handlers import apps
from cocaine.flow.handlers import auth
from cocaine.flow.handlers import buildlogs
from cocaine.flow.handlers import crashlogs
from cocaine.flow.handlers import groups
from cocaine.flow.handlers import hosts
from cocaine.flow.handlers import profiles
from cocaine.flow.handlers import runlists
from cocaine.flow.handlers import utils

from cocaine.flow.flowcloud import FlowCloud
from cocaine.flow.flowcloud import FlowTools
from cocaine.flow.flowcloud import AppUploadInfo
from cocaine.flow.token import Token


class FlowInitializationError(Exception):
    pass


class FlowRestServer(tornado.web.Application):
    def __init__(self, **settings):
        self.logger = logging.getLogger("tornado.application")
        self.logger.debug("Creating FlowRestServer")

        handlers = [
            (r"/flow/v1/profiles/?", profiles.ProfilesList),
            (r"/flow/v1/profiles/(.+)", profiles.Profiles),

            (r"/flow/v1/hosts/(.+)", hosts.Hosts),
            (r"/flow/v1/hosts/?", hosts.HostsList),

            (r"/flow/v1/runlists/(.+)", runlists.Runlists),
            (r"/flow/v1/runlists/?", runlists.RunlistsList),

            (r"/flow/v1/groups/([^/]+)", groups.RoutingGroups),
            (r"/flow/v1/groups/([^/]+)/(.+)", groups.RoutingGroupsPushPop),
            (r"/flow/v1/groups/?", groups.RoutingGroupsList),
            (r"/flow/v1/groupsrefresh/([^/]*)", groups.RoutingGroupsRefresh),

            (r"/flow/v1/crashlogs/([^/]+)", crashlogs.CrashlogsList),
            (r"/flow/v1/crashlogs/([^/]+)/([^/]+)", crashlogs.Crashlogs),

            (r"/flow/v1/buildlogs/", buildlogs.BuildlogsList),
            (r"/flow/v1/buildlogs/(.+)", buildlogs.Buildlogs),

            (r"/flow/v1/signup", auth.SignUp),
            (r"/flow/v1/signin", auth.SignIn),
            (r"/flow/v1/removeuser/([^/]+)", auth.RemoveUser),
            (r"/flow/v1/gentoken", auth.GenToken),

            (r"/flow/v1/apps", apps.AppsList),
            (r"/flow/v1/apps/(?P<app>[^/]+)/(?P<version>.*)", apps.Apps),

            (r"/flow/v1/startapp/(?P<app>.+)/(?P<version>.+)", apps.AppStart),
            (r"/flow/v1/stopapp/(?P<app>.+)/(?P<version>.+)", apps.AppStop),
            (r"/flow/v1/deployapp/(?P<app>.+)/(?P<version>.+)", apps.AppDeploy),

            (r"/flow/ping", utils.Ping),
        ]

        self.cipher = Token(settings['cookie_secret'])
        cocaine_host = settings['cocaine_host']
        cocaine_port = settings['cocaine_port']

        self.logger.info("Connectiong to Cocaine-runtime at %s:%d",
                         cocaine_host, cocaine_port)
        AppUploadInfo.configure(docker=settings['docker'],
                                registry=settings['registry'])
        try:
            FlowTools.instance(host=cocaine_host, port=cocaine_port)
        except Exception as err:  # todo: check other exc types
            self.logger.error("Unable to connect to flow-tools application")
            raise FlowInitializationError("flow-tools is unavailable %s" % err)

        # thread pool for blocking operations
        self._pool = ThreadPool(10)

        tornado.web.Application.__init__(self, handlers, **settings)

    def guest(self):
        return FlowCloud.guest()

    def authorized(self, user_info):
        return FlowCloud.authorized(user_info)

    def run_background(self, func, callback):
        self.logger.debug("Apply %s", func)

        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))
        self._pool.apply_async(func, (), {}, _callback)
