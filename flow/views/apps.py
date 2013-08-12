# encoding: utf-8
#
#    Copyright (c) 2011-2012 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2012 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or
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

from tornado import web

from flow.utils.requesthandler import CocaineRequestHandler
from flow.utils.route import Route
from flow.utils.helpers import get_applications

from cocaine.futures.chain import Chain


@Route(r"/REST/apps")
class Apps(CocaineRequestHandler):

    @web.asynchronous
    def get(self):
        Chain([partial(get_applications,
                       self.finish)])


@Route(r"/flowapi/authorization")
class Sigin(CocaineRequestHandler):

	def post(self, *args):
		user = self.get_argument("user")
		password = self.get_argument("password")
		self.set_cookie("user", "test")