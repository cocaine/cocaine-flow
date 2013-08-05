#
#    Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
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
from flow.utils import helpers

from cocaine.futures.chain import Chain

__all__ = ["Profiles"]


@Route(r'/REST/profiles/?')
class Profiles(CocaineRequestHandler):

    @web.asynchronous
    def get(self, *args, **kwargs):
        name = self.get_argument('name', None)
        if name:
            Chain([partial(helpers.get_profile,
                           self.finish,
                           name)])
        else:
            Chain([partial(helpers.list_profiles,
                           self.finish)])

    @web.asynchronous
    def delete(self, *args, **kwargs):
        name = self.get_argument('name')
        self.log.info("Remove profile %s" % name)
        Chain([partial(helpers.delete_profile,
                       self.finish,
                       name)])

    @web.asynchronous
    def post(self, *args):  # Need ability to upload from raw json profile
        profile = self.request.body
        Chain([partial(helpers.store_profile,
                       self.finish,
                       profile['name'],
                       profile)])

    @web.asynchronous
    def put(self, *args):
        self.post(*args)
