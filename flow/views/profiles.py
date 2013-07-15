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
import json

from tornado import web
import msgpack

from flow.utils.storage import Storage
from flow.utils.requesthandler import CocaineRequestHandler
from flow.utils.route import Route
#from flow.utils.templates import result

from cocaine.tools.actions.profile import List
from cocaine.tools.actions.profile import View
from cocaine.exceptions import CocaineError
from cocaine.exceptions import ServiceError
from cocaine.futures.chain import Chain

__all__ = ["Profiles"]


@Route(r'/profiles/([^/]*)/?')
class Profiles(CocaineRequestHandler):

    @web.addslash
    @web.asynchronous
    def get(self, name=None):
        if name is None or len(name) == 0:
            self.log.info("Request all profiles")
            Chain([partial(do_profiles_view, self)])
        else:
            self.log.info("Request profile %s" % name)
            View(Storage().backend, name=name).execute()\
                .then(partial(do_view, self, name))

    @web.asynchronous
    def delete(self, *args):
        self.finish("pass")

    @web.asynchronous
    def put(self, *args):
        self.finish("pass")


def do_view(obj, name, res):
    try:
        data = res.get()
        obj.write(json.dumps({name: msgpack.unpackb(data)}))
    except CocaineError as err:
        obj.log.error(str(err))
        obj.write(str(err))
    obj.finish()


def do_profiles_view(self):
    try:
        profiles = yield List(Storage().backend).execute()
        views = dict()
        for profile in profiles:
            view = yield View(Storage().backend, name=profile).execute()
            views[profile] = msgpack.unpackb(view)
        self.write(json.dumps(views))
    except ServiceError as err:
        print repr(err)
        self.write(str(err))
    except ValueError as err:
        print repr(err)
    self.finish()