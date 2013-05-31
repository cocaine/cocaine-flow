#!/usr/bin/env python
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
from tornado import options
from tornado.ioloop import IOLoop

from utils.route import Route

import userapi # Add userapi handler to app
import appsapi 

options.parse_command_line()

class SessionManager(object):

    def __init__(self):
        self._cache = dict()

class Application(web.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.session_manager = SessionManager()

app = Application(Route.routes(), debug=True)

app.listen(8080)
IOLoop.instance().start()
