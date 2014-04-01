# encoding: utf-8
#
#    Copyright (c) 2013-2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2013-2014 Other contributors as noted in the AUTHORS file.
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


TOKEN_LIFETIME = 1  # days


class Token(object):
    value_name = "TOKEN"

    def __init__(self, key, lifetime=TOKEN_LIFETIME):
        self.key = key
        self.lifetime = lifetime

    def pack_user(self, user_info):
        assert "password" not in user_info
        value = json.dumps(user_info)
        return web.create_signed_value(self.key, self.value_name, value)

    def valid(self, token):
        raw = web.decode_signed_value(self.key, self.value_name, token, self.lifetime)
        if raw is None:
            raise ValueError("Invalid token")
        else:
            return json.loads(raw)


if __name__ == "__main__":
    t = Token("12312dfdfsf")
    ui = {
        "name": "AAA"
    }

    tok = t.pack_user(t)
    print(tok)

    rui = t.valid(tok)
    assert rui == ui, "%s %s" % (rui, ui)
