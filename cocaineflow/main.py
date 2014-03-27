#!/usr/bin/env python

import tornado.ioloop
import tornado.options

from flow.app import Application

# parse cmdlines
tornado.options.parse_command_line()

if __name__ == "__main__":
    Application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
