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


__all__ = ["Login", "Logout", "User"]


@Route(r"/flow/api/authorization")
class Login(CocaineRequestHandler):

    @web.asynchronous
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        self.set_secure_cookie("user", username)
        Chain([partial(helpers.get_user,
                       self.set_token,
                       username, password)])

    @web.asynchronous
    def get(self):
        self.post()

    def set_token(self, data):
        status = "fail"
        username = None
        res = dict()
        self.set_default_headers()
        try:
            status = data['users'][0]['status']
            username = data['users'][0]['username']
        except KeyError:
            pass
        except Exception:
            pass
        if status == "OK" and username:
            self.set_cookie("user", username)
        else:
            res['reason'] = 'Ivalid username or password'
        res['status'] = status
        self.finish(res)




@Route(r'/logout')
class Logout(CocaineRequestHandler):

    def get(self):
        self.finish()


@Route(r'/user/([^/]*)/?')
class User(CocaineRequestHandler):

    @web.asynchronous
    def post(self, *args):  # POST
        """Create new user"""
        self.log.info("Create new user")
        username = self.get_argument('username')
        password = self.get_argument('password')
        name = self.get_argument('name')
        Chain([partial(helpers.store_user,
                       self.finish,
                       username,
                       password,
                       name=name)])

    @web.asynchronous
    def get(self, name):
        """ Info about users """
        self.log.info("Request user %s info" % name)
        password = self.get_argument('password', None)
        Chain([partial(helpers.get_user,
                       self.finish,
                       name, password)])
