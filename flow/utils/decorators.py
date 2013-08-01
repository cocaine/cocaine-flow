#
#   Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
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

from functools import wraps

__all__ = ["unwrap_result"]


def unwrap_result(func):
    @wraps(func)
    def wrapper(res):
        try:
            func(res.get())
        except Exception as err:
            print err
            func(str(err))
    return wrapper


class RewrapResult(object):

    def __init__(self, result):
        self.res = result

    def get(self):
        return self.res


def dispatch(**gl_kwargs):
    '''
    Wraps Socket.IO methods for dispatching event in handler
    base on method name (get, post, etc)
    '''
    def decorator(func):
        def wrapper(self, method, *args, **kwargs):
            job = gl_kwargs.get(method)
            if job:
                job(self, *args, **kwargs)
            else:
                func(self, method, *args, **kwargs)
        return wrapper
    return decorator
