#
#    Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
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

from tornado import web

from utils.storage import Storage
from utils.requesthandler import CocaineRequestHandler
from utils.route import Route
from utils.templates import result

__all__ = ["Profiles"]

@Route("/profiles")
class Profiles(CocaineRequestHandler):

    @web.asynchronous
    def get(self):
        self.log.info("Request profiles")
        Storage().profiles(self.callback)

    def callback(self, res):
        self.log.info("Return profiles")
        try:
            _data = res.get()
            self.write(result("ok", "success", 0, profiles=_data))
        except Exception as err:
            self.log.error(str(err))
            self.write(result("fail", "error", -2))
        self.finish()


@Route("/profile/([^/]*)/*")
class ProfileView(CocaineRequestHandler):

    @web.asynchronous
    def get(self, name):
        self.log.info("Request %s profile" % name)
        Storage().get_profile(self.callback, name)

    def callback(self, res):
        self.write(res)
        self.finish()
