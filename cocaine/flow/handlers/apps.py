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

from functools import partial

from tornado import gen
from tornado import web

from cocaine.flow.handlers import AuthRequiredCocaineHandler
from cocaine.flow.flowcloud import AppUploadInfo
from cocaine.flow.temprepo import unpack_archive

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
        # unpack body in thread pool and return
        # instance of TempDir
        # todo: it might be better to unpack in flow-tools
        # for using remote cocaine-runtime
        self.tempdir = yield gen.Task(self.run_background,
                                      partial(unpack_archive,
                                              self.request.body))
        if self.tempdir is None:
            raise Exception("Unable to unpack body")

        upl_info = AppUploadInfo(appname, version, self.tempdir.path)
        # clean tempdir after the finish of request
        self.on_finish = self.tempdir.clean

        # flow-tools cocaine future object
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
            self.finish("Unknown error")
