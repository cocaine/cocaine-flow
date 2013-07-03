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

from utils.requesthandler import CocaineRequestHandler
from utils.route import Route
from utils.templates import result

__all__ = ["Login"]

@Route('/login')
class Login(CocaineRequestHandler):

    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.write(result("ok", "all good", 0, k=1, b=2))
        self.finish()

    def get(self):
        self.write(result("fail", "use POST", 0))
        self.finish()


@Route('/logout')
class Logout(CocaineRequestHandler):

    def get(self):
        self.clear_cookie("username")
        self.write(result("ok", "logout successfully", 0))
        self.finish()


