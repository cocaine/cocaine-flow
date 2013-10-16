#!/usr/bin/env python
""" Profile operations """

from cocaine.worker import Worker

from profile import *

W = Worker()

W.run({"get": get,
	   "all": p_list,
	   "store": store,
	   "delete": delete})
