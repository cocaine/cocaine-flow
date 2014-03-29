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

from tornado import gen

from cocaine.flow.handlers import AuthRequiredCocaineHandler


class RoutingGroups(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        result = yield self.fw.group_read(name)
        self.send_json(result)

    @gen.coroutine
    def post(self, name):
        yield self.fw.group_create(name)
        self.ok()

    @gen.coroutine
    def put(self, name):
        yield self.post(name)

    @gen.coroutine
    def delete(self, name):
        yield self.fw.group_remove(name)
        self.ok()


class RoutingGroupsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        result = yield self.fw.group_list()
        self.send_json(result)


class RoutingGroupsPushPop(AuthRequiredCocaineHandler):
    @gen.coroutine
    def put(self, group, app):
        weight = self.get_argument("weight")
        yield self.fw.group_pushapp(group, app, weight)
        self.ok()

    @gen.coroutine
    def delete(self, group, app):
        yield self.fw.group_popapp(group, app)
        self.ok()


class RoutingGroupsRefresh(AuthRequiredCocaineHandler):
    @gen.coroutine
    def post(self, name):
        yield self.fw.group_refresh(name)
        self.ok()
