#!/usr/bin/env python
""" Profile operations """

from cocaine.worker import Worker

from profile import *

W = Worker()


def ping(request, response):
    yield request.read()
    response.write("OK")
    response.close()

W.run({"get": get,
       "all": p_list,
       "store": store,
       "delete": delete,
       "ping": ping})
