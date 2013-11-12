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

import logging

from tornado import ioloop

from cocaine.services import Service
from cocaine.futures.chain import source
from cocaine.tools.actions import app
from cocaine.exceptions import ServiceError

logger = logging.getLogger()


def start_pinger(period):
    ioloop.IOLoop.current().add_callback(pinger)
    timer = ioloop.PeriodicCallback(pinger, period * 1000)
    timer.start()


@source
def ping_application(node, name):
    try:
        res = yield app.Start(node, name, "default").execute()
        logger.debug(res)
        application = Service(name, blockingConnect=False)
        yield application.connect()
        isOK = yield application.enqueue("ping", "")
        logger.info(isOK)
    except ServiceError as err:
        logger.error(err)
    except Exception as err:
        logger.error(err)


@source
def pinger():
    try:
        logger.debug("Ping backend applications")
        node = Service("node", blockingConnect=False)
        yield node.connect()
    except Exception as err:
        logger.error("Backend is not available %s" % err)
    else:
        for name in ("flow-app", "flow-commit", "flow-profile"):
            ping_application(node, name)
