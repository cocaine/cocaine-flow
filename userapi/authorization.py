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

from tornado import web
from tornado.options import options
from utils.route import Route
from utils.storage import Storage

__all__ = ["Login", "Logout"]

@Route(r"/login", isREST=True)
class Login(web.RequestHandler):

    def get(self):
        self.write("Hello, world")
        self.set_secure_cookie(options.AUTHORIZATION_COOKIE, "sdsfsf")

@Route(r"/logout", isREST=True)
class Logout(web.RequestHandler):

    def get(self):
        self.write("Hello, world")
        self.clear_cookie(options.AUTHORIZATION_COOKIE)

@Route(r"/Create")
class CreateUser(web.RequestHandler):

    @web.asynchronous
    def get(self):
        s = Storage()
        s.create_user("test", "test", self)