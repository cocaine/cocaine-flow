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

from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger

namespace_prefix = "flow-users@"
HOSTS_TAG = ["flow-host"]

logger = Logger()

namespace_prefix = "flow-hosts@"


class HostDB(object):
    def __init__(self, storage, namespace):
        self.namespace = namespace_prefix + namespace
        self.storage = storage

    @asynchronous
    def hosts(self):
        yield self.storage.find(self.namespace, HOSTS_TAG)

    @asynchronous
    def add(self, hostname):
        yield self.storage.write(self.namespace, hostname,
                                 hostname, HOSTS_TAG)

    @asynchronous
    def remove(self, hostname):
        yield self.storage.remove(self.namespace,
                                  hostname)
