# encoding: utf-8
#
#    Copyright (c) 2011-2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
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

import json

from tornado import web

from cocaine.flow.flowcloud import FlowCloud


AuthHeaderName = "Authorization"


class CocaineHanler(web.RequestHandler):

    def prepare(self):
        self.fw = FlowCloud.guest()

    def send_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

    def ok(self):
        self.send_json({})

    def write_error(self, *args, **kwargs):
        # hijack exception here
        super(CocaineHanler, self).write_error(*args, **kwargs)


class AuthRequiredCocaineHandler(CocaineHanler):
    def prepare(self):
        # check Authorization header
        try:
            token = self.request.headers[AuthHeaderName]
            self.fw = FlowCloud.authorized(token)
            return
        except KeyError:
            pass
        #
        # TBD: cookies
        #
        raise web.HTTPError(403)

    def get_current_user(self):
        return self.user
