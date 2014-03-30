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

from tornado import gen
from tornado import web

from cocaine.flow.handlers import AuthRequiredCocaineHandler
from cocaine.flow.flowcloud import AppUploadInfo

from cocaine.exceptions import ChokeEvent
from cocaine.exceptions import ServiceError


class AppsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        apps = yield self.fw.app_list()
        self.send_json(apps)


class Apps(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, appname, version):
        info = yield self.fw.app_info(appname, version)
        self.send_json(info)

    @gen.coroutine
    @web.asynchronous
    def post(self, appname, version):
        # todo: unpack body in thread pool
        upl_info = AppUploadInfo(appname, version,
                                 "/Users/noxiouz/Documents/github/cocaine-flow/testapp")
        fut = self.fw.app_upload(upl_info)
        fut.then(self.on_chunk)

    def on_chunk(self, r):
        try:
            item = r.get()
            self.write(item)
            self.flush()
        except ChokeEvent:
            self.logger.info("Close stream successfully")
            self.finish()
        except ServiceError as err:
            self.logger.error(err)
            self.finish("Error occured while uploading")
        except Exception as err:
            self.logger.error(err)

