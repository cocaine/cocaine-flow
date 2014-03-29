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

import logging

import tornado.web

from cocaine.flow.handlers import auth
from cocaine.flow.handlers import buildlogs
from cocaine.flow.handlers import crashlogs
from cocaine.flow.handlers import groups
from cocaine.flow.handlers import hosts
from cocaine.flow.handlers import profiles
from cocaine.flow.handlers import runlists

logger = logging.getLogger("tornado.application")


class FlowRestServer(tornado.web.Application):
    def __init__(self):
        logger.info("Create FlowRestServer")
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
        ]

        settings = dict(
            cookie_secret='11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
            debug=True
        )

        tornado.web.Application.__init__(self, handlers, **settings)
