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
from cocaine.services import Service
from cocaine.tools.tools import NodeInfoAction


from utils.route import Route
from utils.decorators import authorization_require

__all__ = ["Info"]

node = Service("node")
storage = Service("storage")

@Route(r"/Apps")
class Info(web.RequestHandler):

    @authorization_require
    @web.asynchronous
    def get(self):
        info = NodeInfoAction(node)
        info.execute().bind(self.on_info, self.on_error)

    def on_info(self, chunk):
        self.write(chunk)
        self.finish()

    def on_error(self, excep):
        self.write(str(excep))
        self.finish()
