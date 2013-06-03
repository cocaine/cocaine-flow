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

from tornado.options import options

__all__ = ["authorization_require", "CocaineCoroutine"]

def authorization_require(func):
    def wrapper(self, *args, **kwargs):
        if self.get_secure_cookie(options.AUTHORIZATION_COOKIE):
            return func(self, *args, **kwargs)
        else:
            self.write("authorization_require")
            self.finish()
    return wrapper

class _Coroutine(object):

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.obj = func(*args, **kwargs)
            try:
                f = self.obj.next()
                f.bind(self.push, self.error, self.push)
            except StopIteration as err:
                pass
            except Exception as err:
                print err
        return wrapper

    def push(self, chunk=None):
        try:
            f = self.obj.send(chunk)
            f.bind(self.push, self.error, self.push)
        except StopIteration as err:
            pass

    def error(self, err):
        try:
            f = self.obj.throw(err)
            f.bind(self.push, self.error, self.push)
        except StopIteration as err:
            pass

def CocaineCoroutine(func):
    """ Wrapper for coroutine based API
    of cocaine-framework-python.
    Make it easy to using services into coroutines
    """
    return _Coroutine()(func)