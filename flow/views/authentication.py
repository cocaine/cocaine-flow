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

import json
from functools import partial

from tornado import web

from flow.utils.requesthandler import CocaineRequestHandler
from flow.utils.route import Route
from flow.utils.storage import Storage
from flow.utils.templates import result

from cocaine.exceptions import ChokeEvent


__all__ = ["Login", "Logout"]


@Route(r'/login')
class Login(CocaineRequestHandler):

    @web.asynchronous
    def post(self):
        username = self.get_argument("username")
        #password = self.get_argument("password")
        self.set_secure_cookie("username", username)
        self.write(result("ok", "all good", 0))
        self.finish()

    def get(self):
        self.write(result("fail", "use POST", 0))
        self.finish()


@Route(r'/logout')
class Logout(CocaineRequestHandler):

    def get(self):
        self.clear_cookie("username")
        self.write(result("ok", "logout successfully", 0))
        self.finish()


@Route(r'/user/([^/]*)/?')
class User(CocaineRequestHandler):

    @web.asynchronous
    def post(self, *args):  # POST
        """Create new user"""
        password = self.get_argument("password")
        print password
        name = self.get_argument("username")
        print name
        self.log.info("Emit user creation %s" % name)
        Storage().create_user(partial(on_create_user, self), name, password)

    @web.addslash
    @web.asynchronous
    def get(self, name=None):
        """ Info about users """
        self.log.info("Request user %s info" % name)
        Storage().find_user(partial(on_find_user, self), name)

    @web.asynchronous
    def delete(self, name):
        """Delete user"""
        Storage().remove_user(partial(on_remove_user, self), name)

    def put(self, name):
        self.write(name)


def on_create_user(self, res):
    try:
        res.get()
    except ChokeEvent:
        self.write(result("ok", "Create user successfully", 0))
    except Exception as err:
        self.log.exception("Creation user error %s" % err)
        self.write(result("fail", "Unable to create user", 1))
    else:
        self.write(result("fail", "User already exists", 1))
    finally:
        self.finish()


def on_find_user(self, res):
    data = res.get()
    # Drow provate fields
    res = list()
    for item in data:
        item.pop("passwd", None)
        res.append(item)
    print res
    self.write(json.dumps(res))
    self.finish()


def on_remove_user(self, res):
    try:
        print res.get()
    except Exception as err:
        print err
    self.write("DONE")
    self.finish()
