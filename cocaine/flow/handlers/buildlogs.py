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

from tornado import gen

from cocaine.flow.handlers import AuthRequiredCocaineHandler


class Buildlogs(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        buildlog = yield self.fw.buildlog_read(name)
        self.write(buildlog)


class BuildlogsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        buildlogs = yield self.fw.buildlog_list(self.user)
        self.send_json(buildlogs)
