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

from tornado.web import url

#
#   Remake of tornado.tools
#   https://github.com/truemped/tornadotools/blob/master/tornadotools/route.py
#

class Route(object):

    _routes = list()

    def __init__(self, route, name=None, host=".*$", initialize=None, isREST=False):
        self.route = route # route path
        self.host = host # host pattern
        self.name = name # for reverse_url name mapping
        self.initialize = initialize or {} # url placeholders for web.url
        self.isREST = isREST

    def __call__(self, request_handler):
        name = self.name or request_handler.__name__
        spec = url(self.route, request_handler, self.initialize, name=name)
        self._routes.append({'host': self.host, 'spec': spec})
        if self.isREST:
            spec = url("/REST%s"  % self.route, request_handler, self.initialize, name="REST_%s" % name)
            self._routes.append({'host': self.host, 'spec': spec})
        return request_handler

    @classmethod
    def routes(cls):
        return [route['spec'] for route in cls._routes]

