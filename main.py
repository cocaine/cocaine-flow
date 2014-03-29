#!/usr/bin/env python

import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options

from cocaine.flow.app import FlowRestServer

define('port', default=8888, help='run on the given port', type=int)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(FlowRestServer())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
